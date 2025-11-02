from typing import Optional
from ..extensions import db
from .models import Log, ActionType


class LogRepository:
    @staticmethod
    def create(
        action: ActionType,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None
    ) -> Log:
        log = Log(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log

