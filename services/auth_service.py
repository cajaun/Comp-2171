from __future__ import annotations

from datetime import datetime, timezone

from data.models import User
from services.base import ServiceBase
from services.security import hash_password, verify_password
from services.view_models import UserSummary


class AuthService(ServiceBase):
    def authenticate(self, username: str, password: str) -> UserSummary | None:
        username = username.strip()
        password = password.strip()

        if not username or not password:
            raise ValueError("Please enter both username and password.")

        with self.session_scope() as session:
            user = session.query(User).filter(User.username == username).first()
            if not user or not verify_password(password, user.password_hash):
                return None

            if user.password_hash != hash_password(password):
                user.password_hash = hash_password(password)

            user.last_login = datetime.now(timezone.utc)
            session.flush()
            return UserSummary(
                user_id=user.user_id,
                username=user.username,
                role=user.role,
                last_login=user.last_login,
                created_at=user.created_at,
            )
