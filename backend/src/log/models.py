import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db


class ActionType(str, Enum):
    LOGIN = "login"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"


class Log(db.Model):
    __tablename__ = "logs"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    action: Mapped[ActionType] = mapped_column(
        SAEnum(ActionType), 
        nullable=False,
        index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), 
        nullable=True,
        index=True,
        comment="ID of the user who performed the action"
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(50), 
        nullable=True,
        comment="Type of resource affected (user, project, task, etc.)"
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(36), 
        nullable=True,
        comment="ID of the affected resource"
    )
    details: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True,
        comment="Additional details about the action (JSON string)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "action": self.action.value,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

