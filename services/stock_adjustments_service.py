from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from data.models import Item, StockAdjust, User
from services.base import ServiceBase
from services.view_models import AdjustmentRecord, AdjustmentStats, ItemOption


class StockAdjustmentService(ServiceBase):
    ALLOWED_ROLES = {"Admin", "Staff", "Manager"}

    def list_adjustments(self) -> list[AdjustmentRecord]:
        with self.session_scope() as session:
            adjustments = (
                session.query(StockAdjust)
                .options(joinedload(StockAdjust.item), joinedload(StockAdjust.user))
                .order_by(StockAdjust.created_at.desc())
                .all()
            )
            return [
                AdjustmentRecord(
                    adjust_id=adjustment.adjust_id,
                    item_name=adjustment.item.name if adjustment.item else "Unknown",
                    adjust_type=adjustment.adjust_type,
                    quantity=adjustment.quantity or 0,
                    reason=adjustment.reason or "",
                    user_name=adjustment.user.username if adjustment.user else "Unknown",
                    created_at=adjustment.created_at,
                )
                for adjustment in adjustments
            ]

    def get_adjustment_stats(self) -> AdjustmentStats:
        with self.session_scope() as session:
            adjustments = session.query(StockAdjust).all()
            items = {item.item_id: item.name for item in session.query(Item).all()}

        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        week_count = sum(1 for adjustment in adjustments if adjustment.created_at and adjustment.created_at >= week_ago)
        today_count = sum(
            1 for adjustment in adjustments if adjustment.created_at and adjustment.created_at >= today_start
        )
        increases = sum(1 for adjustment in adjustments if adjustment.adjust_type == "Increase")
        decreases = sum(1 for adjustment in adjustments if adjustment.adjust_type == "Decrease")

        most_adjusted = "-"
        counts = Counter(adjustment.item_id for adjustment in adjustments if adjustment.item_id)
        if counts:
            item_id, count = counts.most_common(1)[0]
            item_name = items.get(item_id)
            if item_name:
                most_adjusted = f"{item_name} ({count})"

        return AdjustmentStats(
            week=week_count,
            today=today_count,
            increases=increases,
            decreases=decreases,
            most_adjusted=most_adjusted,
        )

    def list_items(self) -> list[ItemOption]:
        with self.session_scope() as session:
            items = session.query(Item).order_by(Item.name.asc()).all()
            return [ItemOption(item_id=item.item_id, name=item.name) for item in items]

    def record_adjustment(
        self,
        actor_user_id: int,
        item_id: int,
        adjust_type: str,
        quantity: int,
        reason: str,
    ) -> AdjustmentRecord:
        adjust_type = adjust_type.strip().title()
        reason = reason.strip()
        quantity = int(quantity)
        if adjust_type not in {"Increase", "Decrease"}:
            raise ValueError("Adjustment type must be Increase or Decrease")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if not reason:
            raise ValueError("Reason required")

        with self.session_scope() as session:
            user = session.get(User, actor_user_id)
            if not user or user.role not in self.ALLOWED_ROLES:
                raise PermissionError("User is not authorized to record stock adjustments")

            item = session.get(Item, item_id)
            if not item:
                raise ValueError("Item not found")

            if adjust_type == "Increase":
                item.current_stock += quantity
            else:
                if item.current_stock < quantity:
                    raise ValueError("Insufficient stock")
                item.current_stock -= quantity

            adjustment = StockAdjust(
                item_id=item_id,
                user_id=user.user_id,
                adjust_type=adjust_type,
                quantity=quantity,
                reason=reason,
                created_at=datetime.now(timezone.utc),
            )
            session.add(adjustment)
            session.flush()
            return AdjustmentRecord(
                adjust_id=adjustment.adjust_id,
                item_name=item.name,
                adjust_type=adjustment.adjust_type,
                quantity=adjustment.quantity,
                reason=adjustment.reason,
                user_name=user.username,
                created_at=adjustment.created_at,
            )
