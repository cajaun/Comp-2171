from __future__ import annotations

from data.models import Config
from services.base import ServiceBase
from services.view_models import ConfigEntry


class SettingsService(ServiceBase):
    DEFAULTS = (
        ("default_reorder_level", "Default Reorder Level", "10"),
        ("report_default_format", "Report Default Format", "CSV"),
        ("sm_threshold_days", "Slow Moving Threshold (Days)", "30"),
        ("notifications_enabled", "Notifications Enabled", "True"),
    )

    def get_settings(self) -> list[tuple[str, str, str]]:
        with self.session_scope() as session:
            configs = {
                cfg.parameter_name: cfg.parameter_value
                for cfg in session.query(Config).all()
            }
            return [
                (key, label, configs.get(key, default))
                for key, label, default in self.DEFAULTS
            ]

    def save_settings(self, values: dict[str, str]) -> None:
        with self.session_scope() as session:
            for key, _, default in self.DEFAULTS:
                value = values.get(key, default).strip()
                cfg = session.query(Config).filter_by(parameter_name=key).first()
                if cfg:
                    cfg.parameter_value = value
                else:
                    session.add(Config(parameter_name=key, parameter_value=value))

    def get_logs(self) -> list[ConfigEntry]:
        with self.session_scope() as session:
            configs = session.query(Config).order_by(Config.updated_at.desc()).all()
            return [
                ConfigEntry(
                    parameter_name=cfg.parameter_name,
                    parameter_value=cfg.parameter_value,
                    updated_at=cfg.updated_at,
                )
                for cfg in configs
            ]
