from __future__ import annotations

from datetime import datetime, timezone

from data.models import User
from services.base import ServiceBase
from services.security import hash_password
from services.view_models import UserSummary


class UserService(ServiceBase):
    ALLOWED_ROLES = {"Admin", "Staff", "Manager"}

    def list_users(self) -> list[UserSummary]:
        with self.session_scope() as session:
            users = session.query(User).order_by(User.username.asc()).all()
            return [self._to_summary(user) for user in users]

    def get_user(self, user_id: int) -> UserSummary | None:
        with self.session_scope() as session:
            user = session.get(User, user_id)
            return self._to_summary(user) if user else None

    def create_user(self, username: str, password: str, role: str) -> UserSummary:
        username = username.strip()
        role = self._normalize_role(role)
        if not username:
            raise ValueError("Username is required")
        if not password.strip():
            raise ValueError("Password is required")

        with self.session_scope() as session:
            user = User(
                username=username,
                password_hash=hash_password(password.strip()),
                role=role,
                created_at=datetime.now(timezone.utc),
            )
            session.add(user)
            session.flush()
            return self._to_summary(user)

    def update_user(self, user_id: int, username: str, password: str, role: str) -> UserSummary:
        username = username.strip()
        role = self._normalize_role(role)
        if not username:
            raise ValueError("Username is required")

        with self.session_scope() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("User not found")

            user.username = username
            user.role = role
            if password.strip():
                user.password_hash = hash_password(password.strip())

            session.flush()
            return self._to_summary(user)

    def delete_user(self, user_id: int) -> None:
        with self.session_scope() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            session.delete(user)

    def _normalize_role(self, role: str) -> str:
        normalized = role.strip().title()
        if normalized not in self.ALLOWED_ROLES:
            raise ValueError("Role must be Admin, Staff, or Manager")
        return normalized

    def _to_summary(self, user: User) -> UserSummary:
        return UserSummary(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            last_login=user.last_login,
            created_at=user.created_at,
        )
