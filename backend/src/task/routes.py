from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import TaskService
from ..http_responses.responses import success, created, not_found, unprocessable_entity, forbidden
from ..log.service import LogService
from ..log.models import ActionType


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.post("")
@jwt_required()
def create_task():
    """
    Create new task
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - title
              - description
              - project_id
            properties:
              title:
                type: string
                example: Task Title
              description:
                type: string
                example: Task description
              project_id:
                type: string
                example: "project-uuid-here"
              assignee_id:
                type: string
                example: "user-uuid-here"
    responses:
      201:
        description: Task created successfully
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
                    title:
                      type: string
                    description:
                      type: string
                    status:
                      type: string
                      enum: [pending, in_progress, done, awaiting_reassignment]
                    project_id:
                      type: string
                    assignee_id:
                      type: string
      401:
        description: Not authenticated
      404:
        description: Project not found
    """
    try:
        data = request.get_json() or {}
        requester_id = get_jwt_identity()
        task = TaskService.create_task(requester_id, data)
        LogService.log_action(action=ActionType.TASK_CREATED, user_id=requester_id, resource_type="task", resource_id=str(task.id))
        LogService.log_info("Task created successfully", context={"task_id": str(task.id), "project_id": data.get("project_id")})
        return created(data=task.to_dict())
    except ValueError as e:
        LogService.log_error("Failed to create task", error=e, context={"project_id": data.get("project_id")})
        return not_found(str(e)) if "not found" in str(e).lower() else unprocessable_entity(str(e))


@tasks_bp.get("/project/<project_id>")
@jwt_required()
def list_tasks(project_id: str):
    """
    List project tasks
    ---
    tags:
      - Tasks
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
        description: List of tasks
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  title:
                    type: string
                  description:
                    type: string
                  status:
                    type: string
                  project_id:
                    type: string
                  assignee_id:
                    type: string
      401:
        description: Not authenticated
    """
    return success(data=[t.to_dict() for t in TaskService.list_tasks(project_id, get_jwt_identity())])


@tasks_bp.patch("/<task_id>/status")
@jwt_required()
def update_status(task_id: str):
    """
    Update task status
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: task_id
        required: true
        schema:
          type: string
        description: Task ID
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - status
            properties:
              status:
                type: string
                enum: [pending, in_progress, done, awaiting_reassignment]
                example: in_progress
    responses:
      200:
        description: Status updated successfully
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
                    title:
                      type: string
                    status:
                      type: string
                    project_id:
                      type: string
                    assignee_id:
                      type: string
      401:
        description: Not authenticated
      403:
        description: Only the assignee can update the task
      404:
        description: Task not found
    """
    try:
        data = request.get_json() or {}
        requester_id = get_jwt_identity()
        task = TaskService.update_status(task_id, requester_id, data.get("status"))
        LogService.log_action(action=ActionType.TASK_UPDATED, user_id=requester_id, resource_type="task", resource_id=task_id, details={"new_status": data.get("status")})
        LogService.log_info("Task status updated", context={"task_id": task_id, "new_status": data.get("status")})
        return success(data=task.to_dict())
    except ValueError as e:
        LogService.log_error("Failed to update task", error=e, context={"task_id": task_id})
        return not_found(str(e))
    except PermissionError as e:
        LogService.log_error("Permission denied to update task", error=e, context={"task_id": task_id})
        return forbidden(str(e))


@tasks_bp.patch("/<task_id>/assignee")
@jwt_required()
def reassign_task(task_id: str):
    """
    Reassign task to a new assignee
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: task_id
        required: true
        schema:
          type: string
        description: Task ID
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              assignee_id:
                type: string
                nullable: true
                example: "user-uuid-here"
                description: New assignee ID (null to unassign)
    responses:
      200:
        description: Task reassigned successfully
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
                    title:
                      type: string
                    description:
                      type: string
                    status:
                      type: string
                    project_id:
                      type: string
                    assignee_id:
                      type: string
                      nullable: true
      401:
        description: Not authenticated
      403:
        description: Only admin, manager or project owner can reassign tasks
      404:
        description: Task or project not found
    """
    try:
        data = request.get_json() or {}
        requester_id = get_jwt_identity()
        new_assignee_id = data.get("assignee_id")
        task = TaskService.reassign_task(task_id, requester_id, new_assignee_id)
        LogService.log_action(action=ActionType.TASK_UPDATED, user_id=requester_id, resource_type="task", resource_id=task_id, details={"reassigned_to": new_assignee_id})
        LogService.log_info("Task reassigned successfully", context={"task_id": task_id, "new_assignee_id": new_assignee_id})
        return success(data=task.to_dict())
    except ValueError as e:
        LogService.log_error("Failed to reassign task", error=e, context={"task_id": task_id})
        return not_found(str(e)) if "not found" in str(e).lower() else unprocessable_entity(str(e))
    except PermissionError as e:
        LogService.log_error("Permission denied to reassign task", error=e, context={"task_id": task_id})
        return forbidden(str(e))
