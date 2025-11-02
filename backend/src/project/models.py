import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Enum as SAEnum, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db
from ..soft_delete import SoftDeleteMixin


class ProjectStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


project_members = Table(
    "project_members",
    db.metadata,
    db.Column("project_id", String(36), ForeignKey("projects.id"), primary_key=True),
    db.Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
)


class Project(db.Model, SoftDeleteMixin):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus), default=ProjectStatus.PLANNED, nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects_owned")
    members = relationship("User", secondary=project_members)
    tasks = relationship("Task", back_populates="project")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "members": [m.id for m in self.members],
        }
