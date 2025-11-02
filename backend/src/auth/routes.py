from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..user.service import UserService
from ..access_control.decorators import require_roles
from ..http_responses.responses import success, created, unauthorized
from ..log.service import LogService
from ..log.models import ActionType


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """
    User authentication
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - email
              - password
            properties:
              email:
                type: string
                format: email
                example: admin@example.com
              password:
                type: string
                example: admin123
    responses:
      200:
        description: Successful login
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: object
                  properties:
                    access_token:
                      type: string
                    refresh_token:
                      type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = UserService.authenticate(email, password)
    if not user:
        LogService.log_warning("Login failed: invalid credentials", context={"email": email})
        return unauthorized("Invalid credentials")
    access = create_access_token(identity=str(user.id), additional_claims={"role": user.role.value})
    refresh = create_refresh_token(identity=str(user.id))
    LogService.log_action(action=ActionType.LOGIN, user_id=str(user.id))
    LogService.log_info("User logged in successfully", context={"user_id": str(user.id), "email": email})
    return success(data={"access_token": access, "refresh_token": refresh})


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    responses:
      200:
        description: New access token generated
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: object
                  properties:
                    access_token:
                      type: string
      401:
        description: Invalid or expired token
    """
    user_id = get_jwt_identity()
    user = UserService.get_by_id(user_id)
    access = create_access_token(identity=str(user.id), additional_claims={"role": user.role.value})
    return success(data={"access_token": access})


@auth_bp.post("/register")
@jwt_required()
@require_roles(["admin", "manager"])
def register():
    """
    Register new user
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - email
              - password
            properties:
              name:
                type: string
                example: John Doe
              email:
                type: string
                format: email
                example: john@example.com
              password:
                type: string
                example: password123
              role:
                type: string
                enum: [admin, manager, member]
                example: member
    responses:
      201:
        description: User created successfully
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
        description: Insufficient permissions (requires Admin or Manager)
    """
    data = request.get_json() or {}
    user = UserService.create_user(**data)
    LogService.log_action(action=ActionType.USER_CREATED, user_id=str(user.id), resource_type="user", resource_id=str(user.id))
    LogService.log_info("New user created", context={"user_id": str(user.id), "email": user.email})
    return created(data=user.to_dict())
