import enum
from typing import Optional
from sqlalchemy import Column, String, Enum, Boolean
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from app.models.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STANDARD = "standard"


class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name: Optional[str] = Column(String(50), nullable=True)
    last_name: Optional[str] = Column(String(50), nullable=True)
    role: UserRole = Column(
        Enum(UserRole),
        default=UserRole.STANDARD,
        nullable=False
    )
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
