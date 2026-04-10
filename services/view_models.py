from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CategoryOption:
    category_id: int
    name: str


@dataclass(frozen=True)
class ItemOption:
    item_id: int
    name: str


@dataclass(frozen=True)
class UserSummary:
    user_id: int
    username: str
    role: str
    last_login: datetime | None
    created_at: datetime | None


@dataclass(frozen=True)
class ItemSummary:
    item_id: int
    name: str
    category_id: int | None
    category_name: str
    price: float
    current_stock: int
    unit: str
    reorder_level: int


@dataclass(frozen=True)
class InventoryStats:
    total: int
    low: int
    out: int
    categories: int


@dataclass(frozen=True)
class CategorySummary:
    category_id: int
    name: str
    description: str
    item_count: int


@dataclass(frozen=True)
class CategoryStats:
    total: int
    most_items: str
    most_valuable: str
    low_stock: int


@dataclass(frozen=True)
class AdjustmentRecord:
    adjust_id: int
    item_name: str
    adjust_type: str
    quantity: int
    reason: str
    user_name: str
    created_at: datetime | None


@dataclass(frozen=True)
class AdjustmentStats:
    week: int
    today: int
    increases: int
    decreases: int
    most_adjusted: str


@dataclass(frozen=True)
class ConditionRecord:
    condition_id: int
    item_name: str
    condition_type: str
    quantity: int
    reason: str
    cost_impact: float
    recorded_at: datetime | None


@dataclass(frozen=True)
class ConditionStats:
    loss_value: float
    loss_count: int
    top_reason: str
    most_damaged: str


@dataclass(frozen=True)
class ReportRecord:
    report_id: int
    report_type: str
    format_type: str
    generated_at: datetime | None
    user_name: str


@dataclass(frozen=True)
class ReportDownload:
    filename: str
    content: bytes | str
    is_binary: bool


@dataclass(frozen=True)
class SlowMovingFlagRecord:
    sm_id: int
    item_name: str
    stock_quantity: int
    last_sold_date: datetime | None
    days_since: int | None
    suggested_action: str


@dataclass(frozen=True)
class SlowMovingStats:
    total: int
    value_locked: float
    oldest: str
    overstock: int


@dataclass(frozen=True)
class SlowMovingConfig:
    days_threshold: int
    quantity_threshold: int


@dataclass(frozen=True)
class ConfigEntry:
    parameter_name: str
    parameter_value: str
    updated_at: datetime | None


@dataclass(frozen=True)
class StockByCategoryPoint:
    category: str
    count: int
    percentage: float


@dataclass(frozen=True)
class MonthlyAdjustmentPoint:
    label: str
    stock_in: int
    stock_out: int
    manual_adjustments: int = 0


@dataclass(frozen=True)
class ConditionSummaryPoint:
    label: str
    quantity: int


@dataclass(frozen=True)
class DashboardSnapshot:
    total_products: int
    new_products: int
    total_categories: int
    low_stock_count: int
    damaged_total: int
    damaged_recent: int
    total_stock_units: int = 0
    stock_trend_percent: float = 0.0
    condition_good_percentage: int = 100
    stock_by_category: list[StockByCategoryPoint] = field(default_factory=list)
    monthly_adjustments: list[MonthlyAdjustmentPoint] = field(default_factory=list)
    condition_summary: list[ConditionSummaryPoint] = field(default_factory=list)
