from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import joinedload

from data.models import Item, ItemCondition, User
from services.base import ServiceBase
from services.view_models import ConditionRecord, ConditionStats, ItemOption


class ConditionService(ServiceBase):
    ALLOWED_ROLES = {"Admin", "Staff", "Manager"}

    def list_conditions(self) -> list[ConditionRecord]:
        with self.session_scope() as session:
            conditions = (
                session.query(ItemCondition)
                .options(joinedload(ItemCondition.item))
                .order_by(ItemCondition.recorded_at.desc())
                .all()
            )
            return [
                ConditionRecord(
                    condition_id=condition.condition_id,
                    item_name=condition.item.name if condition.item else "Unknown",
                    condition_type=condition.condition_type,
                    quantity=condition.quantity or 0,
                    reason=condition.reason or "",
                    cost_impact=float(condition.cost_impact or 0),
                    recorded_at=condition.recorded_at,
                )
                for condition in conditions
            ]

    def get_condition_stats(self) -> ConditionStats:
        with self.session_scope() as session:
            conditions = session.query(ItemCondition).all()
            items = {item.item_id: item.name for item in session.query(Item).all()}

        total_loss = sum(float(condition.cost_impact or 0) for condition in conditions)
        total_count = len(conditions)

        top_reason = "-"
        reasons = Counter(condition.reason for condition in conditions if condition.reason)
        if reasons:
            reason, count = reasons.most_common(1)[0]
            top_reason = f"{reason} ({count})"

        most_damaged = "-"
        item_counts = Counter(condition.item_id for condition in conditions if condition.item_id)
        if item_counts:
            item_id, count = item_counts.most_common(1)[0]
            item_name = items.get(item_id)
            if item_name:
                most_damaged = f"{item_name} ({count})"

        return ConditionStats(
            loss_value=total_loss,
            loss_count=total_count,
            top_reason=top_reason,
            most_damaged=most_damaged,
        )

    def list_items(self) -> list[ItemOption]:
        with self.session_scope() as session:
            items = session.query(Item).order_by(Item.name.asc()).all()
            return [ItemOption(item_id=item.item_id, name=item.name) for item in items]

    def record_condition(
        self,
        actor_user_id: int,
        item_id: int,
        condition_type: str,
        quantity: int,
        reason: str,
    ) -> ConditionRecord:
        quantity = int(quantity)
        condition_type = condition_type.strip().title()
        reason = reason.strip()
        if condition_type not in {"Damaged", "Expired", "Lost"}:
            raise ValueError("Condition must be Damaged, Expired, or Lost")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if not reason:
            raise ValueError("Reason required")

        with self.session_scope() as session:
            user = session.get(User, actor_user_id)
            if not user or user.role not in self.ALLOWED_ROLES:
                raise PermissionError("User is not authorized to record item conditions")

            item = session.get(Item, item_id)
            if not item:
                raise ValueError("Item not found")
            if item.current_stock < quantity:
                raise ValueError("Insufficient stock")

            item.current_stock -= quantity
            condition = ItemCondition(
                item_id=item_id,
                condition_type=condition_type,
                quantity=quantity,
                reason=reason,
                cost_impact=(item.price or 0) * quantity,
                recorded_at=datetime.now(timezone.utc),
            )
            session.add(condition)
            session.flush()
            return ConditionRecord(
                condition_id=condition.condition_id,
                item_name=item.name,
                condition_type=condition.condition_type,
                quantity=condition.quantity,
                reason=condition.reason,
                cost_impact=float(condition.cost_impact or 0),
                recorded_at=condition.recorded_at,
            )
