from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..access_control.decorators import require_roles
from .service import ProjectService
from ..http_responses.responses import success, created, not_found, no_content, bad_request, forbidden, unprocessable_entity
from ..log.service import LogService
from ..log.models import ActionType


projects_bp = Blueprint("projects", __name__)


@projects_bp.post("")
@jwt_required()
@require_roles(["manager", "admin"])  
def create_project():
    """
    Create new project
    ---
    tags:
      - Projects
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
              - description
            properties:
              name:
                type: string
                example: My Project
              description:
                type: string
                example: Project description
    responses:
      201:
        description: Project created successfully
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
                    description:
                      type: string
                    status:
                      type: string
                      enum: [planned, in_progress, completed]
                    owner_id:
                      type: string
                    members:
                      type: array
                      items:
                        type: string
      401:
        description: Not authenticated
      403:
        description: Insufficient permissions (requires Manager or Admin)
    """
    owner_id = get_jwt_identity()
    data = request.get_json() or {}
    project = ProjectService.create_project(owner_id, data)
    LogService.log_action(action=ActionType.PROJECT_CREATED, user_id=owner_id, resource_type="project", resource_id=str(project.id))
    LogService.log_info("Project created successfully", context={"project_id": str(project.id), "owner_id": owner_id})
    return created(data=project.to_dict())


@projects_bp.get("")
@jwt_required()
def list_projects():
    """
    List user projects
    ---
    tags:
      - Projects
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of projects
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
                  description:
                    type: string
                  status:
                    type: string
                  owner_id:
                    type: string
                  members:
                    type: array
                    items:
                      type: string
      401:
        description: Not authenticated
    """
    return success(data=[p.to_dict() for p in ProjectService.list_projects_for_user(get_jwt_identity())])


@projects_bp.get("/<project_id>")
@jwt_required()
def get_project(project_id: str):
    """
    Get project by ID
    ---
    tags:
      - Projects
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: string
        description: Project ID
    responses:
      200:
        description: Project data
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
                    description:
                      type: string
                    status:
                      type: string
                    owner_id:
                      type: string
                    members:
                      type: array
                      items:
                        type: string
      401:
        description: Not authenticated
      404:
        description: Project not found
    """
    project = ProjectService.get_by_id(project_id)
    if not project:
        return not_found()
    return success(data=project.to_dict())


@projects_bp.patch("/<project_id>")
@jwt_required()
@require_roles(["manager", "admin"])  
def update_project(project_id: str):
    """
    Update project
    ---
    tags:
      - Projects
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: string
        description: Project ID
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
              description:
                type: string
                example: Updated description
              status:
                type: string
                enum: [planned, in_progress, completed]
                example: in_progress
    responses:
      200:
        description: Project updated
        content:
          application/json:
            schema:
              type: object
      401:
        description: Not authenticated
      403:
        description: Only the owner can update the project
      404:
        description: Project not found
    """
    try:
        data = request.get_json() or {}
        requester_id = get_jwt_identity()
        project = ProjectService.update_project(project_id, requester_id, data)
        LogService.log_action(action=ActionType.PROJECT_UPDATED, user_id=requester_id, resource_type="project", resource_id=project_id)
        LogService.log_info("Project updated successfully", context={"project_id": project_id})
        return success(data=project.to_dict())
    except ValueError as e:
        LogService.log_error("Failed to update project", error=e, context={"project_id": project_id})
        return not_found(str(e)) if "not found" in str(e).lower() else unprocessable_entity(str(e))
    except PermissionError as e:
        LogService.log_error("Permission denied to update project", error=e, context={"project_id": project_id})
        return forbidden(str(e))


@projects_bp.delete("/<project_id>")
@jwt_required()
@require_roles(["manager", "admin"])  
def delete_project(project_id: str):
    """
    Delete project
    ---
    tags:
      - Projects
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: string
        description: Project ID
    responses:
      204:
        description: Project deleted successfully
      401:
        description: Not authenticated
      403:
        description: Only the owner can delete the project
    """
    try:
        requester_id = get_jwt_identity()
        ProjectService.delete_project(project_id, requester_id)
        LogService.log_action(action=ActionType.PROJECT_DELETED, user_id=requester_id, resource_type="project", resource_id=project_id)
        LogService.log_info("Project deleted successfully", context={"project_id": project_id})
        return no_content()
    except PermissionError as e:
        LogService.log_error("Permission denied to delete project", error=e, context={"project_id": project_id})
        return forbidden(str(e))


@projects_bp.post("/<project_id>/members")
@jwt_required()
@require_roles(["manager", "admin"])  
def add_member(project_id: str):
    """
    Add member to project
    ---
    tags:
      - Projects
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: string
        description: Project ID
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - user_id
            properties:
              user_id:
                type: string
                example: "user-uuid-here"
    responses:
      204:
        description: Member added successfully
      401:
        description: Not authenticated
      403:
        description: Only the owner can add members
      404:
        description: Project or user not found
    """
    try:
        data = request.get_json() or {}
        requester_id = get_jwt_identity()
        ProjectService.add_member(project_id, requester_id, data.get("user_id"))
        LogService.log_action(action=ActionType.MEMBER_ADDED, user_id=requester_id, resource_type="project", resource_id=project_id, details={"added_user_id": data.get("user_id")})
        LogService.log_info("Member added to project", context={"project_id": project_id, "member_id": data.get("user_id")})
        return no_content()
    except ValueError as e:
        LogService.log_error("Failed to add member to project", error=e, context={"project_id": project_id})
        return not_found(str(e)) if "not found" in str(e).lower() else unprocessable_entity(str(e))
    except PermissionError as e:
        LogService.log_error("Permission denied to add member", error=e, context={"project_id": project_id})
        return forbidden(str(e))


@projects_bp.delete("/<project_id>/members/<user_id>")
@jwt_required()
@require_roles(["manager", "admin"])  
def remove_member(project_id: str, user_id: str):
    """
    Remove member from project
    ---
    tags:
      - Projects
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: project_id
        required: true
        schema:
          type: string
        description: Project ID
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: User ID
    responses:
      204:
        description: Member removed successfully
      401:
        description: Not authenticated
      403:
        description: Only the owner can remove members
      404:
        description: Project or user not found
    """
    try:
        requester_id = get_jwt_identity()
        ProjectService.remove_member(project_id, requester_id, user_id)
        LogService.log_action(action=ActionType.MEMBER_REMOVED, user_id=requester_id, resource_type="project", resource_id=project_id, details={"removed_user_id": user_id})
        LogService.log_info("Member removed from project", context={"project_id": project_id, "member_id": user_id})
        return no_content()
    except ValueError as e:
        LogService.log_error("Failed to remove member from project", error=e, context={"project_id": project_id})
        return not_found(str(e))
    except PermissionError as e:
        LogService.log_error("Permission denied to remove member", error=e, context={"project_id": project_id})
        return forbidden(str(e))
