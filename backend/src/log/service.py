import logging
from typing import Optional
from datetime import datetime
from .repository import LogRepository
from .models import ActionType


app_logger = logging.getLogger("app")


class LogService:
    @staticmethod
    def log_action(
        action: ActionType,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        import json
        
        details_json = json.dumps(details) if details else None
        
        LogRepository.create(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details_json
        )
    
    @staticmethod
    def log_info(message: str, context: Optional[dict] = None) -> None:
        context_str = f" | Context: {context}" if context else ""
        app_logger.info(f"[{datetime.utcnow().isoformat()}] {message}{context_str}")
    
    @staticmethod
    def log_error(message: str, error: Optional[Exception] = None, context: Optional[dict] = None) -> None:
        error_str = f" | Error: {str(error)}" if error else ""
        context_str = f" | Context: {context}" if context else ""
        app_logger.error(f"[{datetime.utcnow().isoformat()}] {message}{error_str}{context_str}")
    
    @staticmethod
    def log_warning(message: str, context: Optional[dict] = None) -> None:
        context_str = f" | Context: {context}" if context else ""
        app_logger.warning(f"[{datetime.utcnow().isoformat()}] {message}{context_str}")
    
    @staticmethod
    def log_debug(message: str, context: Optional[dict] = None) -> None:
        context_str = f" | Context: {context}" if context else ""
        app_logger.debug(f"[{datetime.utcnow().isoformat()}] {message}{context_str}")

