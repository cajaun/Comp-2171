import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from data.models import Base, StockAdjust, User
from services.auth_service import AuthService
from services.category_service import CategoryService
from services.damaged_expired_service import ConditionService
from services.inventory_service import InventoryService
from services.report_service import ReportService
from services.security import hash_password
from services.slow_moving_service import SlowMovingService
from services.stock_adjustments_service import StockAdjustmentService
from services.user_service import UserService


class TestCoreLogic(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.category_service = CategoryService(self.Session)
        self.inventory_service = InventoryService(self.Session)
        self.user_service = UserService(self.Session)
        self.auth_service = AuthService(self.Session)
        self.stock_adjustment_service = StockAdjustmentService(self.Session)
        self.condition_service = ConditionService(self.Session)
        self.report_service = ReportService(self.Session)
        self.slow_moving_service = SlowMovingService(self.Session)

        self.category = self.category_service.create_category("Test Category", "For testing")
        self.admin = self.user_service.create_user("admin", "admin123", "Admin")
        self.staff = self.user_service.create_user("staff", "staff123", "Staff")

        session = self.Session()
        try:
            guest = User(username="guest", password_hash=hash_password("guest"), role="Guest")
            session.add(guest)
            session.commit()
            session.refresh(guest)
            self.guest_id = guest.user_id
        finally:
            session.close()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_case_1_add_product_success(self):
        item = self.inventory_service.create_item(
            name="Cornbeef",
            category_id=self.category.category_id,
            price=3500.0,
            stock=35,
            unit="2 box",
            reorder_level=5,
        )
        self.assertEqual(item.name, "Cornbeef")
        self.assertEqual(item.price, 3500.0)
        self.assertEqual(item.current_stock, 35)
        self.assertEqual(item.unit, "2 box")

    def test_case_2_add_product_missing_fields(self):
        with self.assertRaises(ValueError):
            self.inventory_service.create_item(
                name="Cornbeef",
                category_id=self.category.category_id,
                price=10,
                stock=1,
                unit="",
                reorder_level=1,
            )

    def test_fr1_duplicate_name_prevention(self):
        self.inventory_service.create_item("Duplicate Item", self.category.category_id, 10, 10, "box", 2)
        with self.assertRaises(IntegrityError):
            self.inventory_service.create_item("Duplicate Item", self.category.category_id, 20, 20, "box", 2)

    def test_case_3_stock_adjust_authorized(self):
        item = self.inventory_service.create_item("Jasmine Rice", self.category.category_id, 100, 100, "bag", 10)
        adjustment = self.stock_adjustment_service.record_adjustment(
            actor_user_id=self.admin.user_id,
            item_id=item.item_id,
            adjust_type="Increase",
            quantity=50,
            reason="New Shipment received",
        )
        updated = self.inventory_service.get_item(item.item_id)
        self.assertEqual(updated.current_stock, 150)
        self.assertEqual(adjustment.user_name, "admin")

    def test_case_4_stock_adjust_unauthorized(self):
        item = self.inventory_service.create_item("Jasmine Rice", self.category.category_id, 100, 100, "bag", 10)
        with self.assertRaises(PermissionError):
            self.stock_adjustment_service.record_adjustment(
                actor_user_id=self.guest_id,
                item_id=item.item_id,
                adjust_type="Increase",
                quantity=50,
                reason="New Shipment received",
            )

    def test_case_5_stock_adjust_missing_fields(self):
        item = self.inventory_service.create_item("Flour", self.category.category_id, 100, 100, "bag", 10)
        with self.assertRaises(ValueError):
            self.stock_adjustment_service.record_adjustment(
                actor_user_id=self.admin.user_id,
                item_id=item.item_id,
                adjust_type="",
                quantity=50,
                reason="Restock",
            )

    def test_case_6_condition_tracking_success(self):
        item = self.inventory_service.create_item("Bread", self.category.category_id, 100, 20, "pack", 5)
        condition = self.condition_service.record_condition(
            actor_user_id=self.staff.user_id,
            item_id=item.item_id,
            condition_type="Expired",
            quantity=12,
            reason="Past sell-by date",
        )
        updated = self.inventory_service.get_item(item.item_id)
        self.assertEqual(updated.current_stock, 8)
        self.assertEqual(condition.condition_type, "Expired")

    def test_case_7_condition_tracking_insufficient_stock(self):
        item = self.inventory_service.create_item("Bread 2", self.category.category_id, 100, 10, "pack", 5)
        with self.assertRaises(ValueError):
            self.condition_service.record_condition(
                actor_user_id=self.staff.user_id,
                item_id=item.item_id,
                condition_type="Expired",
                quantity=12,
                reason="Past sell-by date",
            )
        updated = self.inventory_service.get_item(item.item_id)
        self.assertEqual(updated.current_stock, 10)

    def test_case_8_report_generation_success(self):
        self.inventory_service.create_item("Report Item", self.category.category_id, 50, 100, "unit", 10)
        report = self.report_service.generate_report("Inventory", "CSV", self.admin.user_id)
        self.assertIsNotNone(report)
        download = self.report_service.get_report_download(report.report_id)
        self.assertIn("Report Item", download.content)

    def test_case_9_report_generation_failure(self):
        with self.assertRaises(ValueError):
            self.report_service.generate_report("UnknownType", "CSV", self.admin.user_id)

    def test_case_10_slow_moving_detection(self):
        item = self.inventory_service.create_item("Slow Mover", self.category.category_id, 10, 200, "unit", 10)
        session = self.Session()
        try:
            session.add(
                StockAdjust(
                    item_id=item.item_id,
                    user_id=self.admin.user_id,
                    adjust_type="Decrease",
                    quantity=1,
                    reason="Sale",
                    created_at=datetime.now(timezone.utc) - timedelta(days=100),
                )
            )
            session.commit()
        finally:
            session.close()

        self.slow_moving_service.run_analysis(90, 150)
        flags = self.slow_moving_service.list_flags()
        self.assertEqual(len(flags), 1)
        self.assertIn("Slow Moving", flags[0].suggested_action)

    def test_case_11_12_slow_moving_invalid_input(self):
        with self.assertRaises(ValueError):
            self.slow_moving_service.run_analysis("hjk", 100)

    def test_case_13_search_success(self):
        self.inventory_service.create_item("Milk", self.category.category_id, 10, 50, "box", 10)
        results = self.inventory_service.list_items(search_text="Milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Milk")

    def test_case_14_search_no_match(self):
        self.inventory_service.create_item("Milk", self.category.category_id, 10, 50, "box", 10)
        results = self.inventory_service.list_items(search_text="XJF9999")
        self.assertEqual(len(results), 0)

    def test_authentication_updates_last_login(self):
        user = self.auth_service.authenticate("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")
        self.assertIsNotNone(user.last_login)


if __name__ == "__main__":
    unittest.main()
