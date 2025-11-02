from src.user.repository import UserRepository
from src.user.models import UserRole
from src.project.models import ProjectStatus
from src.task.models import TaskStatus


def test_create_project_success(client, manager_user, manager_token, project_data):
    resp = client.post(
        "/api/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == project_data["name"]
    assert data["status"] == ProjectStatus.PLANNED.value


def test_create_project_forbidden_as_member(client, member_token, project_data):
    resp = client.post(
        "/api/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_list_projects_for_user(client, manager_user, member_user, auth_token, app):
    from src.cache import cache
    cache.client = None
    
    token_manager = auth_token(manager_user.email, "pass")
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {token_manager}"},
    )
    project_id = resp.get_json()["id"]
    
    client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member_user.id},
        headers={"Authorization": f"Bearer {token_manager}"},
    )
    
    token_member = auth_token(member_user.email, "pass")
    resp = client.get("/api/projects", headers={"Authorization": f"Bearer {token_member}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1


def test_get_project_success(client, manager_user, manager_token):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    resp = client.get(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Project 1"


def test_get_project_not_found(client, manager_token):
    resp = client.get("/api/projects/invalid-id", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 404


def test_update_project_success(client, manager_user, manager_token):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    resp = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated Project", "description": "Updated Description"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Updated Project"


def test_update_project_forbidden_not_owner(client, manager_user, auth_token):
    manager2 = UserRepository.create("Manager2", "manager2@x.com", "pass", role=UserRole.MANAGER.value)
    
    token1 = auth_token(manager_user.email, "pass")
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    project_id = resp.get_json()["id"]
    
    token2 = auth_token(manager2.email, "pass")
    resp = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated Project"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert resp.status_code == 403


def test_update_project_forbidden_completed(client, manager_user, member_user, manager_token):
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
    
    resp = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 422


def test_delete_project_success(client, manager_user, manager_token):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    resp = client.delete(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 204
    
    resp = client.get(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 404


def test_add_member_success(client, manager_user, member_user, manager_token):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    resp = client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member_user.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 204


def test_add_member_forbidden_completed_project(client, manager_user, member_user, manager_token):
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
        status=TaskStatus.DONE,
    )
    TaskRepository.create(task)
    
    resp = client.patch(
        f"/api/projects/{project_id}",
        json={"status": ProjectStatus.COMPLETED.value},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    
    resp = client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member2.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 422


def test_remove_member_success(client, manager_user, member_user, manager_token):
    resp = client.post(
        "/api/projects",
        json={"name": "Project 1", "description": "Description 1"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    project_id = resp.get_json()["id"]
    
    client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member_user.id},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    
    resp = client.delete(
        f"/api/projects/{project_id}/members/{member_user.id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 204
