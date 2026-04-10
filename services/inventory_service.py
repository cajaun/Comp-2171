from __future__ import annotations

from sqlalchemy.orm import joinedload

from data.models import Category, Item
from services.base import ServiceBase
from services.view_models import CategoryOption, InventoryStats, ItemSummary


class InventoryService(ServiceBase):
    def list_items(
        self,
        search_text: str = "",
        category_name: str | None = None,
        stock_filter: str | None = None,
    ) -> list[ItemSummary]:
        with self.session_scope() as session:
            items = session.query(Item).options(joinedload(Item.category)).all()
            results = [self._to_summary(item) for item in items]

        search_value = search_text.strip().lower()
        if search_value:
            results = [item for item in results if search_value in item.name.lower()]

        if category_name:
            results = [item for item in results if item.category_name == category_name]

        if stock_filter == "In Stock":
            results = [item for item in results if item.current_stock > 0]
        elif stock_filter == "Low Stock":
            results = [item for item in results if item.current_stock < item.reorder_level]
        elif stock_filter == "Out of Stock":
            results = [item for item in results if item.current_stock == 0]

        return results

    def list_categories(self) -> list[CategoryOption]:
        with self.session_scope() as session:
            categories = session.query(Category).order_by(Category.name.asc()).all()
            return [
                CategoryOption(category_id=category.category_id, name=category.name)
                for category in categories
            ]

    def get_item(self, item_id: int) -> ItemSummary | None:
        with self.session_scope() as session:
            item = session.get(Item, item_id)
            return self._to_summary(item) if item else None

    def create_item(
        self,
        name: str,
        category_id: int,
        price: float,
        stock: int,
        unit: str,
        reorder_level: int,
    ) -> ItemSummary:
        self._validate_item_fields(name, price, stock, unit, reorder_level)
        with self.session_scope() as session:
            item = Item(
                name=name.strip(),
                category_id=category_id,
                price=float(price),
                current_stock=int(stock),
                unit=unit.strip(),
                reorder_level=int(reorder_level),
            )
            session.add(item)
            session.flush()
            session.refresh(item)
            return self._to_summary(item)

    def update_item(
        self,
        item_id: int,
        name: str,
        category_id: int,
        price: float,
        stock: int,
        unit: str,
        reorder_level: int,
    ) -> ItemSummary:
        self._validate_item_fields(name, price, stock, unit, reorder_level)
        with self.session_scope() as session:
            item = session.get(Item, item_id)
            if not item:
                raise ValueError("Item not found")

            item.name = name.strip()
            item.category_id = category_id
            item.price = float(price)
            item.current_stock = int(stock)
            item.unit = unit.strip()
            item.reorder_level = int(reorder_level)
            session.flush()
            session.refresh(item)
            return self._to_summary(item)

    def delete_item(self, item_id: int) -> None:
        with self.session_scope() as session:
            item = session.get(Item, item_id)
            if not item:
                raise ValueError("Item not found")
            session.delete(item)

    def get_inventory_stats(self) -> InventoryStats:
        items = self.list_items()
        with self.session_scope() as session:
            categories_count = session.query(Category).count()

        return InventoryStats(
            total=len(items),
            low=sum(1 for item in items if item.current_stock < item.reorder_level),
            out=sum(1 for item in items if item.current_stock == 0),
            categories=categories_count,
        )

    def _validate_item_fields(
        self,
        name: str,
        price: float,
        stock: int,
        unit: str,
        reorder_level: int,
    ) -> None:
        if not name.strip():
            raise ValueError("Name is required")
        if not unit.strip():
            raise ValueError("Unit is required")
        if float(price) < 0:
            raise ValueError("Price must be 0 or greater")
        if int(stock) < 0:
            raise ValueError("Stock must be 0 or greater")
        if int(reorder_level) < 0:
            raise ValueError("Reorder level must be 0 or greater")

    def _to_summary(self, item: Item) -> ItemSummary:
        category_name = item.category.name if item.category else "-"
        reorder_level = item.reorder_level or 10
        unit = item.unit or "-"
        return ItemSummary(
            item_id=item.item_id,
            name=item.name,
            category_id=item.category_id,
            category_name=category_name,
            price=float(item.price or 0),
            current_stock=int(item.current_stock or 0),
            unit=unit,
            reorder_level=int(reorder_level),
        )
