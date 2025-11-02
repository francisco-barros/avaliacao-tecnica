from functools import wraps
from flask_jwt_extended import get_jwt_identity
from .service import LogService
from .models import ActionType
from typing import Optional


def log_action_to_db(
    action: ActionType,
    resource_type: Optional[str] = None,
    get_resource_id: Optional[callable] = None
):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                response = fn(*args, **kwargs)
                
                user_id = None
                try:
                    user_id = get_jwt_identity()
                except RuntimeError:
                    pass
                
                resource_id = None
                if get_resource_id:
                    try:
                        resource_id = get_resource_id(response)
                    except Exception:
                        pass
                
                try:
                    LogService.log_action(
                        action=action,
                        user_id=user_id,
                        resource_type=resource_type,
                        resource_id=resource_id
                    )
                except Exception:
                    pass
                
                return response
                
            except Exception as e:
                if "Failed to log action to database" not in str(e):
                    raise
                return fn(*args, **kwargs)
        
        return wrapper
    return decorator

