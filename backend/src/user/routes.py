from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..access_control.decorators import require_roles
from .service import UserService
from ..http_responses.responses import success, not_found, no_content, unprocessable_entity, forbidden
from ..log.service import LogService
from ..log.models import ActionType


users_bp = Blueprint("users", __name__)


@users_bp.get("")
@jwt_required()
@require_roles(["admin", "manager"])  
def list_users():
    """
    List all users
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of users
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  email:
                    type: string
                  role:
                    type: string
      401:
        description: Not authenticated
      403:
        description: Insufficient permissions (requires Admin or Manager)
    """
    return success(data=[u.to_dict() for u in UserService.list_users()])


@users_bp.get("/<user_id>")
@jwt_required()
@require_roles(["admin", "manager"])  
def get_user(user_id: str):
    """
    Get user by ID
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: User ID
    responses:
      200:
        description: User data
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: object
                  properties:
                    id:
                      type: string
                    name:
                      type: string
                    email:
                      type: string
                    role:
                      type: string
      401:
        description: Not authenticated
      403:
        description: Insufficient permissions
      404:
        description: User not found
    """
    user = UserService.get_by_id(user_id)
    if not user:
        return not_found()
    return success(data=user.to_dict())


@users_bp.patch("/<user_id>")
@jwt_required()
def update_user(user_id: str):
    """
    Update user
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: User ID
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                example: Updated Name
              email:
                type: string
                format: email
                example: updated@example.com
              role:
                type: string
                enum: [admin, manager, member]
                example: manager
    responses:
      200:
        description: User updated
        content:
          application/json:
            schema:
              type: object
      401:
        description: Not authenticated
      403:
        description: Forbidden - only admin can update other users or change roles
      404:
        description: User not found
    """
    try:
        requester_id = str(get_jwt_identity())
        claims = get_jwt()
        requester_role = claims.get("role")
        is_admin = requester_role == "admin"
        
        data = request.get_json() or {}
        user_id_str = str(user_id)
        
        if not is_admin and requester_id != user_id_str:
            LogService.log_warning("Unauthorized user update attempt", context={"requester_id": requester_id, "target_user_id": user_id_str})
            return forbidden("You can only update your own profile")
        
        if not is_admin and "role" in data:
            LogService.log_warning("Unauthorized role update attempt", context={"requester_id": requester_id, "target_user_id": user_id_str})
            return forbidden("Only administrators can change user roles")
        
        user = UserService.update_user(user_id, data)
        LogService.log_action(action=ActionType.USER_UPDATED, user_id=requester_id, resource_type="user", resource_id=user_id)
        LogService.log_info("User updated successfully", context={"user_id": user_id, "requester_id": requester_id})
        return success(data=user.to_dict())
    except ValueError as e:
        LogService.log_error("Failed to update user", error=e, context={"user_id": user_id})
        return not_found(str(e))


@users_bp.delete("/<user_id>")
@jwt_required()
@require_roles(["admin"])  
def delete_user(user_id: str):
    """
    Delete user (soft delete)
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: User ID
    responses:
      204:
        description: User deleted successfully. Performs soft delete and handles cascading updates:
        - Projects owned by the user have their owner_id set to None
        - Tasks assigned to the user have their status set to AWAITING_REASSIGNMENT and assignee_id set to None
      401:
        description: Not authenticated
      403:
        description: Only Admin can delete users
    """
    UserService.delete_user(user_id)
    LogService.log_action(action=ActionType.USER_DELETED, user_id=user_id, resource_type="user", resource_id=user_id)
    LogService.log_info("User deleted successfully", context={"user_id": user_id})
    return no_content()
