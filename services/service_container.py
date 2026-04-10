from __future__ import annotations

from dataclasses import dataclass

from data.db import SessionLocal
from services.auth_service import AuthService
from services.category_service import CategoryService
from services.damaged_expired_service import ConditionService
from services.dashboard_service import DashboardService
from services.inventory_service import InventoryService
from services.report_service import ReportService
from services.settings_service import SettingsService
from services.slow_moving_service import SlowMovingService
from services.stock_adjustments_service import StockAdjustmentService
from services.user_service import UserService


@dataclass(frozen=True)
class ServiceContainer:
    auth: AuthService
    inventory: InventoryService
    categories: CategoryService
    users: UserService
    stock_adjustments: StockAdjustmentService
    conditions: ConditionService
    reports: ReportService
    slow_moving: SlowMovingService
    settings: SettingsService
    dashboard: DashboardService


def build_service_container(session_factory=SessionLocal) -> ServiceContainer:
    return ServiceContainer(
        auth=AuthService(session_factory),
        inventory=InventoryService(session_factory),
        categories=CategoryService(session_factory),
        users=UserService(session_factory),
        stock_adjustments=StockAdjustmentService(session_factory),
        conditions=ConditionService(session_factory),
        reports=ReportService(session_factory),
        slow_moving=SlowMovingService(session_factory),
        settings=SettingsService(session_factory),
        dashboard=DashboardService(session_factory),
    )
