from .repository import ProjectRepository
from ..user.repository import UserRepository
from ..task.repository import TaskRepository
from .models import Project, ProjectStatus
from ..task.models import TaskStatus
from ..cache import cache


class ProjectService:
    @staticmethod
    def _invalidate_project_cache(project: Project):
        cache.delete(f"projects:{project.owner_id}")
        for member in project.members:
            cache.delete(f"projects:{member.id}")

    @staticmethod
    def create_project(owner_id: str, data: dict) -> Project:
        owner = UserRepository.get_by_id(owner_id)
        project = Project(
            name=data.get("name"),
            description=data.get("description"),
            status=ProjectStatus.PLANNED,
            owner_id=owner.id if owner else owner_id,
        )
        project = ProjectRepository.create(project)
        cache.delete(f"projects:{owner_id}")
        return project

    @staticmethod
    def get_by_id(project_id: str) -> Project | None:
        return ProjectRepository.get_by_id(project_id)

    @staticmethod
    def list_projects_for_user(user_id: str) -> list[Project]:
        return ProjectRepository.list_for_user(user_id)

    @staticmethod
    def update_project(project_id: str, requester_id: str, data: dict) -> Project:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            raise ValueError("not found")
        if project.status == ProjectStatus.COMPLETED:
            raise ValueError("completed projects are read-only")
        if requester_id != project.owner_id:
            raise PermissionError("only owner can update project")
        if "name" in data:
            project.name = data["name"]
        if "description" in data:
            project.description = data["description"]
        if "status" in data:
            project.status = ProjectStatus(data["status"])
        project = ProjectRepository.update(project)
        ProjectService._invalidate_project_cache(project)
        return project

    @staticmethod
    def delete_project(project_id: str, requester_id: str) -> None:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return
        if requester_id != project.owner_id:
            raise PermissionError("only owner can delete project")
        ProjectService._invalidate_project_cache(project)
        ProjectRepository.delete(project)

    @staticmethod
    def add_member(project_id: str, requester_id: str, user_id: str) -> None:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            raise ValueError("not found")
        if project.status == ProjectStatus.COMPLETED:
            raise ValueError("completed projects cannot add members")
        if requester_id != project.owner_id:
            raise PermissionError("only owner can add members")
        user = UserRepository.get_by_id(user_id)
        if user and user not in project.members:
            project.members.append(user)
            project = ProjectRepository.update(project)
            cache.delete(f"projects:{user_id}")

    @staticmethod
    def remove_member(project_id: str, requester_id: str, user_id: str) -> None:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            raise ValueError("not found")
        if requester_id != project.owner_id:
            raise PermissionError("only owner can remove members")
        project.members = [m for m in project.members if m.id != user_id]
        ProjectRepository.update(project)
        cache.delete(f"projects:{user_id}")

    @staticmethod
    def recompute_status_if_completed(project_id: str) -> None:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return
        tasks = TaskRepository.list_for_project(project_id)
        if tasks and all(t.status == TaskStatus.DONE for t in tasks):
            project.status = ProjectStatus.COMPLETED
            project = ProjectRepository.update(project)
            ProjectService._invalidate_project_cache(project)
