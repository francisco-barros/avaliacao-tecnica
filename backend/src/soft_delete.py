from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
    """Mixin for models that support soft delete."""
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        index=True
    )
    
    def is_deleted(self) -> bool:
        """Check if the record is deleted."""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a deleted record."""
        self.deleted_at = None

