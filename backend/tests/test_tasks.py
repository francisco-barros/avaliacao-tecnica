import pytest
from src.user.repository import UserRepository
from src.user.models import UserRole
from src.task.models import TaskStatus
from src.project.models import ProjectStatus


def test_create_task_success(client, manager_user, member_user, manager_token, task_data):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    resp = client.post(
        "/api/tasks",
        json={
            **task_data,
            "project_id": project_id,
            "assignee_id": member_user.id,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == task_data["title"]
    assert data["status"] == TaskStatus.PENDING.value


def test_create_task_project_not_found(client, manager_user, member_user, manager_token, task_data):
    resp = client.post(
        "/api/tasks",
        json={
            **task_data,
            "project_id": "invalid-id",
            "assignee_id": member_user.id,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 404


def test_create_task_completed_project(client, manager_user, member_user, manager_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.DONE,
    )
    TaskRepository.create(task)
    
    resp = client.patch(
        f"/api/projects/{project_id}",
        json={"status": ProjectStatus.COMPLETED.value},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    
    resp = client.post(
        "/api/tasks",
        json={
            "title": "Task 2",
            "description": "Task description",
            "project_id": project_id,
            "assignee_id": member_user.id,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 422


def test_list_tasks_success(client, manager_user, member_user, manager_token):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    client.post(
        "/api/tasks",
        json={
            "title": "Task 1",
            "description": "Description",
            "project_id": project_id,
            "assignee_id": member_user.id,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    
    resp = client.get(f"/api/tasks/project/{project_id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"


def test_update_task_status_success(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    token_member = auth_token(member_user.email, "pass")
    resp = client.patch(
        f"/api/tasks/{task.id}/status",
        json={"status": TaskStatus.IN_PROGRESS.value},
        headers={"Authorization": f"Bearer {token_member}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == TaskStatus.IN_PROGRESS.value
    assert data["assignee_id"] == member_user.id


def test_update_task_status_forbidden_not_assignee(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    member2 = UserRepository.create("Member2", "member2@x.com", "pass", role=UserRole.MEMBER.value)
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    token_member2 = auth_token(member2.email, "pass")
    resp = client.patch(
        f"/api/tasks/{task.id}/status",
        json={"status": TaskStatus.DONE.value},
        headers={"Authorization": f"Bearer {token_member2}"},
    )
    assert resp.status_code == 403


def test_update_task_status_not_found(client, member_token):
    resp = client.patch(
        "/api/tasks/invalid-id/status",
        json={"status": TaskStatus.DONE.value},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 404


def test_update_task_status_to_awaiting_reassignment_removes_assignee(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    token_member = auth_token(member_user.email, "pass")
    resp = client.patch(
        f"/api/tasks/{task.id}/status",
        json={"status": TaskStatus.AWAITING_REASSIGNMENT.value},
        headers={"Authorization": f"Bearer {token_member}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == TaskStatus.AWAITING_REASSIGNMENT.value
    assert data["assignee_id"] is None
    
    task = TaskRepository.get_by_id(task.id)
    assert task.assignee_id is None


def test_project_auto_completes_when_all_tasks_done(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    from src.project.service import ProjectService
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task1 = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.DONE,
    )
    TaskRepository.create(task1)
    
    task2 = Task(
        title="Task 2",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.DONE,
    )
    TaskRepository.create(task2)
    
    ProjectService.recompute_status_if_completed(project_id)
    
    token_member = auth_token(member_user.email, "pass")
    
    resp = client.get(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {token_member}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == ProjectStatus.COMPLETED.value


def test_reassign_task_success_as_admin(client, manager_user, member_user, admin_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {auth_token(manager_user.email, 'pass')}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    member2 = UserRepository.create("Member2", "member2@x.com", "pass", role=UserRole.MEMBER.value)
    client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member2.id},
        headers={"Authorization": f"Bearer {auth_token(manager_user.email, 'pass')}"},
    )
    
    resp = client.patch(
        f"/api/tasks/{task.id}/assignee",
        json={"assignee_id": member2.id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["assignee_id"] == member2.id
    
    task = TaskRepository.get_by_id(task.id)
    assert task.assignee_id == member2.id


def test_reassign_task_success_as_manager_or_owner(client, manager_user, member_user, manager_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    member2 = UserRepository.create("Member2", "member2@x.com", "pass", role=UserRole.MEMBER.value)
    client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member2.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    
    resp = client.patch(
        f"/api/tasks/{task.id}/assignee",
        json={"assignee_id": member2.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["assignee_id"] == member2.id


def test_reassign_task_forbidden_as_member(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    member2 = UserRepository.create("Member2", "member2@x.com", "pass", role=UserRole.MEMBER.value)
    token_member = auth_token(member_user.email, "pass")
    
    resp = client.patch(
        f"/api/tasks/{task.id}/assignee",
        json={"assignee_id": member2.id},
        headers={"Authorization": f"Bearer {token_member}"},
    )
    assert resp.status_code == 403


def test_reassign_task_not_found(client, manager_user, member_user, manager_token):
    resp = client.patch(
        "/api/tasks/invalid-id/assignee",
        json={"assignee_id": member_user.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 404


def test_reassign_task_awaiting_reassignment_to_pending(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=None,
        status=TaskStatus.AWAITING_REASSIGNMENT,
    )
    task = TaskRepository.create(task)
    
    member2 = UserRepository.create("Member2", "member2@x.com", "pass", role=UserRole.MEMBER.value)
    client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member2.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    
    resp = client.patch(
        f"/api/tasks/{task.id}/assignee",
        json={"assignee_id": member2.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["assignee_id"] == member2.id
    assert data["status"] == TaskStatus.PENDING.value
    
    task = TaskRepository.get_by_id(task.id)
    assert task.assignee_id == member2.id
    assert task.status == TaskStatus.PENDING


def test_reassign_task_invalid_assignee_not_project_member(client, manager_user, member_user, manager_token, auth_token):
    from src.task.repository import TaskRepository
    from src.task.models import Task
    
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    task = Task(
        title="Task 1",
        description="Description",
        project_id=project_id,
        assignee_id=member_user.id,
        status=TaskStatus.PENDING,
    )
    task = TaskRepository.create(task)
    
    member2 = UserRepository.create("Member2", "member2@x.com", "pass", role=UserRole.MEMBER.value)
    
    resp = client.patch(
        f"/api/tasks/{task.id}/assignee",
        json={"assignee_id": member2.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 422
