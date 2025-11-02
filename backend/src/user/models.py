import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db
from ..soft_delete import SoftDeleteMixin


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class User(db.Model, SoftDeleteMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects_owned = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role.value}
