from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import joinedload

from data.models import Config, Item, SlowMovingOverstock, StockAdjust
from services.base import ServiceBase
from services.view_models import SlowMovingConfig, SlowMovingFlagRecord, SlowMovingStats


class SlowMovingService(ServiceBase):
    def list_flags(self) -> list[SlowMovingFlagRecord]:
        with self.session_scope() as session:
            flags = (
                session.query(SlowMovingOverstock)
                .options(joinedload(SlowMovingOverstock.item))
                .order_by(SlowMovingOverstock.flagged_at.desc())
                .all()
            )
            now = datetime.now(timezone.utc)
            return [
                SlowMovingFlagRecord(
                    sm_id=flag.sm_id,
                    item_name=flag.item.name if flag.item else "Unknown",
                    stock_quantity=flag.stock_quantity or 0,
                    last_sold_date=flag.last_sold_date,
                    days_since=((now - self._coerce_utc(flag.last_sold_date)).days if flag.last_sold_date else None),
                    suggested_action=flag.suggested_action or "",
                )
                for flag in flags
            ]

    def get_stats(self) -> SlowMovingStats:
        with self.session_scope() as session:
            flags = (
                session.query(SlowMovingOverstock)
                .options(joinedload(SlowMovingOverstock.item))
                .all()
            )
            total = len(flags)
            total_value = sum(
                (flag.item.price or 0) * (flag.stock_quantity or 0)
                for flag in flags if flag.item
            )

            oldest = "-"
            if flags:
                now = datetime.now(timezone.utc)
                oldest_flag = min(flags, key=lambda flag: flag.last_sold_date or now)
                if oldest_flag.item and oldest_flag.last_sold_date:
                    days = (now - self._coerce_utc(oldest_flag.last_sold_date)).days
                    oldest = f"{oldest_flag.item.name} ({days}d)"

            overstock_count = sum(
                1 for flag in flags if flag.suggested_action and "Overstock" in flag.suggested_action
            )

            return SlowMovingStats(
                total=total,
                value_locked=float(total_value),
                oldest=oldest,
                overstock=overstock_count,
            )

    def get_configuration(self) -> SlowMovingConfig:
        return SlowMovingConfig(
            days_threshold=int(self._get_config("slow_moving_days", "90")),
            quantity_threshold=int(self._get_config("overstock_threshold", "100")),
        )

    def save_configuration(self, days_threshold: int, quantity_threshold: int) -> None:
        if int(days_threshold) <= 0 or int(quantity_threshold) <= 0:
            raise ValueError("Thresholds must be greater than 0")
        self._save_config("slow_moving_days", str(int(days_threshold)))
        self._save_config("overstock_threshold", str(int(quantity_threshold)))

    def run_analysis(self, days_threshold: int, quantity_threshold: int) -> None:
        days_threshold = int(days_threshold)
        quantity_threshold = int(quantity_threshold)
        if days_threshold <= 0 or quantity_threshold <= 0:
            raise ValueError("Thresholds must be greater than 0")

        with self.session_scope() as session:
            session.query(SlowMovingOverstock).delete()
            items = session.query(Item).all()
            now = datetime.now(timezone.utc)

            for item in items:
                last_sale = (
                    session.query(StockAdjust)
                    .filter(StockAdjust.item_id == item.item_id)
                    .filter(StockAdjust.adjust_type == "Decrease")
                    .order_by(StockAdjust.created_at.desc())
                    .first()
                )
                last_sold_date = (
                    last_sale.created_at
                    if last_sale and last_sale.created_at
                    else item.created_at or now
                )
                if last_sold_date.tzinfo is None:
                    last_sold_date = last_sold_date.replace(tzinfo=timezone.utc)
                days_since = (now - last_sold_date).days

                actions = []
                if days_since > days_threshold:
                    actions.append("Slow Moving")
                if (item.current_stock or 0) > quantity_threshold:
                    actions.append("Overstock")

                if actions:
                    session.add(
                        SlowMovingOverstock(
                            item_id=item.item_id,
                            last_adjust_id=last_sale.adjust_id if last_sale else None,
                            flagged_at=now,
                            last_sold_date=last_sold_date,
                            stock_quantity=item.current_stock,
                            threshold_days=days_threshold,
                            threshold_quantity=quantity_threshold,
                            suggested_action=", ".join(actions),
                        )
                    )

    def _get_config(self, key: str, default: str) -> str:
        with self.session_scope() as session:
            cfg = session.query(Config).filter(Config.parameter_name == key).first()
            return cfg.parameter_value if cfg else default

    def _save_config(self, key: str, value: str) -> None:
        with self.session_scope() as session:
            cfg = session.query(Config).filter(Config.parameter_name == key).first()
            if cfg:
                cfg.parameter_value = value
            else:
                session.add(Config(parameter_name=key, parameter_value=value))

    def _coerce_utc(self, value):
        if value is None or value.tzinfo is not None:
            return value
        return value.replace(tzinfo=timezone.utc)
