from .repository import TaskRepository
from ..project.repository import ProjectRepository
from ..user.repository import UserRepository
from .models import Task, TaskStatus
from ..project.models import ProjectStatus
from ..extensions import socketio
from ..project.service import ProjectService
from ..cache import cache


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
        task = TaskRepository.update(task)
        cache.delete(f"tasks:{task.project_id}")
        ProjectService.recompute_status_if_completed(task.project_id)
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
