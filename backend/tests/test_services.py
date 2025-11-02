import pytest
from src.user.repository import UserRepository
from src.user.service import UserService
from src.project.service import ProjectService
from src.task.service import TaskService
from src.user.models import UserRole
from src.project.models import ProjectStatus
from src.task.models import TaskStatus


@pytest.fixture()
def project_data():
    return {"name": "Project", "description": "Desc"}


def test_user_service_authenticate_success(app, test_user):
    with app.app_context():
        user = UserService.authenticate("test@example.com", "password123")
        assert user is not None
        assert user.email == "test@example.com"


def test_user_service_authenticate_invalid_password(app, test_user):
    with app.app_context():
        user = UserService.authenticate("test@example.com", "wrong")
        assert user is None


def test_user_service_authenticate_invalid_email(app):
    with app.app_context():
        result = UserService.authenticate("invalid@example.com", "password")
        assert result is None


def test_user_service_create_user(app):
    with app.app_context():
        user = UserService.create_user("Test User", "test@example.com", "password123", role=UserRole.ADMIN.value)
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN


def test_user_service_delete_user_cascades(app, manager_user, project_data):
    with app.app_context():
        from src.project.repository import ProjectRepository
        from src.project.models import Project
        from src.task.repository import TaskRepository
        from src.task.models import Task
        
        project = Project(
            name=project_data["name"],
            description=project_data["description"],
            status=ProjectStatus.PLANNED,
            owner_id=manager_user.id,
        )
        project = ProjectRepository.create(project)
        
        task = Task(
            title="Test Task",
            description="Test",
            project_id=project.id,
            assignee_id=manager_user.id,
            status=TaskStatus.PENDING,
        )
        TaskRepository.create(task)
        
        UserService.delete_user(manager_user.id)
        
        project = ProjectRepository.get_by_id(project.id)
        assert project.owner_id is None
        
        task = TaskRepository.get_by_id(task.id)
        assert task.status == TaskStatus.AWAITING_REASSIGNMENT
        assert task.assignee_id is None


def test_project_service_create_project(app, manager_user, project_data):
    with app.app_context():
        project = ProjectService.create_project(manager_user.id, project_data)
        assert project.name == project_data["name"]
        assert project.status == ProjectStatus.PLANNED
        assert project.owner_id == manager_user.id


def test_project_service_list_projects_for_user(app, manager_user, member_user, project_data):
    with app.app_context():
        project = ProjectService.create_project(manager_user.id, project_data)
        ProjectService.add_member(project.id, manager_user.id, member_user.id)
        
        projects = ProjectService.list_projects_for_user(member_user.id)
        assert len(projects) == 1
        assert projects[0].id == project.id


def test_project_service_update_project_not_owner(app, manager_user, project_data):
    with app.app_context():
        other = UserRepository.create("Other", "other@example.com", "pass", role=UserRole.MANAGER.value)
        
        project = ProjectService.create_project(manager_user.id, project_data)
        
        with pytest.raises(PermissionError):
            ProjectService.update_project(project.id, other.id, {"name": "Updated"})


def test_project_service_add_member_not_owner(app, manager_user, member_user, project_data):
    with app.app_context():
        other = UserRepository.create("Other", "other@example.com", "pass", role=UserRole.MANAGER.value)
        
        project = ProjectService.create_project(manager_user.id, project_data)
        
        with pytest.raises(PermissionError):
            ProjectService.add_member(project.id, other.id, member_user.id)


def test_project_service_add_member_completed_project(app, manager_user, member_user, project_data):
    with app.app_context():
        from src.task.repository import TaskRepository
        from src.task.models import Task
        
        project = ProjectService.create_project(manager_user.id, project_data)
        task = Task(
            title="Task",
            description="Desc",
            project_id=project.id,
            assignee_id=member_user.id,
            status=TaskStatus.DONE,
        )
        TaskRepository.create(task)
        ProjectService.recompute_status_if_completed(project.id)
        
        with pytest.raises(ValueError):
            ProjectService.add_member(project.id, manager_user.id, member_user.id)


def test_task_service_create_task_completed_project(app, manager_user, member_user, project_data):
    with app.app_context():
        from src.task.repository import TaskRepository
        from src.task.models import Task
        
        project = ProjectService.create_project(manager_user.id, project_data)
        task = Task(
            title="Task",
            description="Desc",
            project_id=project.id,
            assignee_id=member_user.id,
            status=TaskStatus.DONE,
        )
        TaskRepository.create(task)
        ProjectService.recompute_status_if_completed(project.id)
        
        with pytest.raises(ValueError):
            TaskService.create_task(manager_user.id, {
                "title": "New Task",
                "description": "Desc",
                "project_id": project.id,
                "assignee_id": member_user.id,
            })


def test_task_service_update_status_not_assignee(app, manager_user, member_user, project_data):
    with app.app_context():
        from src.task.repository import TaskRepository
        from src.task.models import Task
        
        member2 = UserRepository.create("Member2", "member2@example.com", "pass", role=UserRole.MEMBER.value)
        
        project = ProjectService.create_project(manager_user.id, project_data)
        task = Task(
            title="Task",
            description="Desc",
            project_id=project.id,
            assignee_id=member_user.id,
            status=TaskStatus.PENDING,
        )
        task = TaskRepository.create(task)
        
        with pytest.raises(PermissionError):
            TaskService.update_status(task.id, member2.id, TaskStatus.DONE.value)
