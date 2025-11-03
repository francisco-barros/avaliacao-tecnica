from .repository import TaskRepository
from ..project.repository import ProjectRepository
from ..user.repository import UserRepository
from .models import Task, TaskStatus
from ..project.models import ProjectStatus
from ..extensions import socketio
from ..project.service import ProjectService
from ..cache import cache
from ..user.models import UserRole


class TaskService:
    @staticmethod
    def create_task(requester_id: str, data: dict) -> Task:
        project = ProjectRepository.get_by_id(data.get("project_id"))
        if not project:
            raise ValueError("project not found")
        if project.status == ProjectStatus.COMPLETED:
            raise ValueError("cannot add tasks to completed projects")
        task = Task(
            title=data.get("title"),
            description=data.get("description"),
            project_id=project.id,
            assignee_id=data.get("assignee_id"),
        )
        task = TaskRepository.create(task)
        cache.delete(f"tasks:{project.id}")
        TaskService.broadcast_progress(project.id)
        return task

    @staticmethod
    def list_tasks(project_id: str, requester_id: str) -> list[Task]:
        cache_key = f"tasks:{project_id}"
        cached = cache.get(cache_key)
        if cached:
            import json
            tasks_data = json.loads(cached)
            return [Task(**{**t, "status": TaskStatus(t["status"])}) for t in tasks_data]
        tasks = TaskRepository.list_for_project(project_id)
        import json
        cache.set(cache_key, json.dumps([t.to_dict() for t in tasks]), ex=60)
        return tasks

    @staticmethod
    def update_status(task_id: str, requester_id: str, status: str) -> Task:
        task = TaskRepository.get_by_id(task_id)
        if not task:
            raise ValueError("not found")
        if task.assignee_id != requester_id:
            raise PermissionError("only assignee can change status")
        task.status = TaskStatus(status)
        if task.status == TaskStatus.AWAITING_REASSIGNMENT:
            task.assignee_id = None
        task = TaskRepository.update(task)
        cache.delete(f"tasks:{task.project_id}")
        ProjectService.recompute_status_if_completed(task.project_id)
        TaskService.broadcast_progress(task.project_id)
        return task

    @staticmethod
    def reassign_task(task_id: str, requester_id: str, new_assignee_id: str | None) -> Task:
        task = TaskRepository.get_by_id(task_id)
        if not task:
            raise ValueError("not found")
        project = ProjectRepository.get_by_id(task.project_id)
        if not project:
            raise ValueError("project not found")
        requester = UserRepository.get_by_id(requester_id)
        if not requester:
            raise PermissionError("requester not found")
        is_admin = requester.role == UserRole.ADMIN
        is_manager = requester.role == UserRole.MANAGER
        is_owner = project.owner_id == requester_id
        if not (is_admin or is_manager or is_owner):
            raise PermissionError("only admin, manager or project owner can reassign tasks")
        if new_assignee_id:
            new_assignee = UserRepository.get_by_id(new_assignee_id)
            if not new_assignee:
                raise ValueError("new assignee not found")
            is_project_member = new_assignee_id in [m.id for m in project.members] or new_assignee_id == project.owner_id
            if not is_project_member:
                raise ValueError("new assignee must be a project member or owner")
        task.assignee_id = new_assignee_id
        if task.status == TaskStatus.AWAITING_REASSIGNMENT and new_assignee_id:
            task.status = TaskStatus.PENDING
        task = TaskRepository.update(task)
        cache.delete(f"tasks:{task.project_id}")
        TaskService.broadcast_progress(task.project_id)
        return task

    @staticmethod
    def broadcast_progress(project_id: str) -> None:
        tasks = TaskRepository.list_for_project(project_id)
        if not tasks:
            percent = 0
        else:
            done = len([t for t in tasks if t.status == TaskStatus.DONE])
            percent = int((done / len(tasks)) * 100)
        socketio.emit("project_progress", {"project_id": project_id, "percent": percent})
