from typing import List
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class User(Base):
    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    image: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user")

class RefreshToken(Base):
    access_token: Mapped[str] = mapped_column(index=True)
    expires_at: Mapped[datetime] = mapped_column()
    refresh_token: Mapped[str] = mapped_column(unique=True, index=True)
    provider: Mapped[str] = mapped_column(nullable=True, default="google")
    is_active: Mapped[bool] = mapped_column(default=False, index=True)
    token_type: Mapped[str] = mapped_column()

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")