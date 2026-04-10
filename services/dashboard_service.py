from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from data.models import Category, Item, ItemCondition, StockAdjust
from services.base import ServiceBase
from services.view_models import (
    ConditionSummaryPoint,
    DashboardSnapshot,
    MonthlyAdjustmentPoint,
    StockByCategoryPoint,
)


class DashboardService(ServiceBase):
    def get_snapshot(self) -> DashboardSnapshot:
        with self.session_scope() as session:
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)

            items = session.query(Item).all()
            total_products = len(items)
            new_products = sum(
                1 for item in items if item.created_at and item.created_at >= thirty_days_ago
            )
            total_categories = session.query(Category).count()
            low_stock_count = sum(
                1 for item in items if item.current_stock < (item.reorder_level or 10)
            )

            damaged_recent = (
                session.query(ItemCondition)
                .filter(ItemCondition.recorded_at >= thirty_days_ago)
                .count()
            )
            damaged_total = session.query(ItemCondition).count()

            stock_rows = (
                session.query(Category.name, func.sum(Item.current_stock))
                .join(Item, Category.category_id == Item.category_id)
                .group_by(Category.name)
                .order_by(func.sum(Item.current_stock).desc())
                .limit(5)
                .all()
            )
            total_stock_all = session.query(func.sum(Item.current_stock)).scalar() or 0
            stock_by_category = [
                StockByCategoryPoint(
                    category=name,
                    count=count or 0,
                    percentage=((count or 0) / total_stock_all) if total_stock_all else 0,
                )
                for name, count in stock_rows
            ]

            adjustment_rows = session.query(StockAdjust).all()
            monthly_buckets: dict[str, dict[str, int]] = defaultdict(
                lambda: {"Increase": 0, "Decrease": 0, "Manual": 0}
            )
            for adjustment in adjustment_rows:
                if not adjustment.created_at:
                    continue
                adjusted_at = self._coerce_utc(adjustment.created_at)
                label = adjusted_at.strftime("%b %Y")
                monthly_buckets[label][adjustment.adjust_type] += adjustment.quantity or 0

            month_starts = []
            for offset in range(5, -1, -1):
                month = now.month - offset
                year = now.year
                while month <= 0:
                    month += 12
                    year -= 1
                month_starts.append(datetime(year, month, 1, tzinfo=timezone.utc))

            monthly_adjustments = [
                MonthlyAdjustmentPoint(
                    label=month_start.strftime("%b"),
                    stock_in=monthly_buckets[month_start.strftime("%b %Y")]["Increase"],
                    stock_out=monthly_buckets[month_start.strftime("%b %Y")]["Decrease"],
                    manual_adjustments=monthly_buckets[month_start.strftime("%b %Y")]["Manual"],
                )
                for month_start in month_starts
            ]

            condition_rows = (
                session.query(ItemCondition.condition_type, func.sum(ItemCondition.quantity))
                .group_by(ItemCondition.condition_type)
                .all()
            )
            good_stock = total_stock_all
            condition_summary = [ConditionSummaryPoint(label="Good", quantity=int(good_stock))]
            condition_summary.extend(
                ConditionSummaryPoint(label=label or "Unknown", quantity=quantity or 0)
                for label, quantity in condition_rows
            )
            total_condition_units = sum(point.quantity for point in condition_summary)
            condition_good_percentage = (
                round((good_stock / total_condition_units) * 100)
                if total_condition_units else 100
            )

            current_month = monthly_adjustments[-1] if monthly_adjustments else None
            previous_month = monthly_adjustments[-2] if len(monthly_adjustments) > 1 else None
            current_net = (current_month.stock_in - current_month.stock_out) if current_month else 0
            previous_net = (previous_month.stock_in - previous_month.stock_out) if previous_month else 0
            if previous_net == 0:
                stock_trend_percent = 100.0 if current_net > 0 else 0.0
            else:
                stock_trend_percent = ((current_net - previous_net) / abs(previous_net)) * 100

            return DashboardSnapshot(
                total_products=total_products,
                new_products=new_products,
                total_categories=total_categories,
                low_stock_count=low_stock_count,
                damaged_total=damaged_total,
                damaged_recent=damaged_recent,
                total_stock_units=int(total_stock_all),
                stock_trend_percent=round(stock_trend_percent, 1),
                condition_good_percentage=int(condition_good_percentage),
                stock_by_category=stock_by_category,
                monthly_adjustments=monthly_adjustments,
                condition_summary=condition_summary,
            )

    def _coerce_utc(self, value):
        if value is None or value.tzinfo is not None:
            return value
        return value.replace(tzinfo=timezone.utc)
