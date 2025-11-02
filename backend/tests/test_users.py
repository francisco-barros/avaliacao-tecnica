from src.user.repository import UserRepository
from src.user.models import UserRole


def test_list_users_as_admin(client, admin_user, auth_token):
    UserRepository.create("User1", "user1@x.com", "pass", role=UserRole.MEMBER.value)
    UserRepository.create("User2", "user2@x.com", "pass", role=UserRole.MEMBER.value)
    
    token = auth_token(admin_user.email, "pass")
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 3


def test_list_users_as_manager(client, manager_token):
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 200


def test_list_users_forbidden_as_member(client, member_token):
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 403


def test_get_user_success(client, admin_token):
    from src.user.repository import UserRepository
    user = UserRepository.create("User", "user@x.com", "pass", role=UserRole.MEMBER.value)
    
    resp = client.get(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["email"] == "user@x.com"


def test_get_user_not_found(client, admin_token):
    resp = client.get("/api/users/invalid-id", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 404


def test_delete_user_success_as_admin(client, admin_token):
    from src.user.repository import UserRepository
    user = UserRepository.create("User", "user@x.com", "pass", role=UserRole.MEMBER.value)
    
    resp = client.delete(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204
    
    resp = client.get(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 404


def test_delete_user_forbidden_as_manager(client, manager_token):
    from src.user.repository import UserRepository
    user = UserRepository.create("User", "user@x.com", "pass", role=UserRole.MEMBER.value)
    
    resp = client.delete(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert resp.status_code == 403


def test_update_user_success_as_admin(client, admin_token):
    from src.user.repository import UserRepository
    user = UserRepository.create("User", "user@x.com", "pass", role=UserRole.MEMBER.value)
    
    resp = client.patch(
        f"/api/users/{user.id}",
        json={"role": UserRole.MANAGER.value},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["role"] == UserRole.MANAGER.value


def test_update_user_forbidden_as_manager(client, manager_token):
    from src.user.repository import UserRepository
    user = UserRepository.create("User", "user@x.com", "pass", role=UserRole.MEMBER.value)
    
    resp = client.patch(
        f"/api/users/{user.id}",
        json={"role": UserRole.MANAGER.value},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 403


def test_update_user_not_found(client, admin_token):
    resp = client.patch(
        "/api/users/invalid-id",
        json={"role": UserRole.MANAGER.value},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


def test_delete_user_cascades_projects(client, admin_token, manager_user):
    from src.project.repository import ProjectRepository
    from src.project.models import Project, ProjectStatus
    
    project = Project(
        name="Test Project",
        description="Test",
        status=ProjectStatus.PLANNED,
        owner_id=manager_user.id,
    )
    ProjectRepository.create(project)
    
    resp = client.delete(f"/api/users/{manager_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204
    
    project = ProjectRepository.get_by_id(project.id)
    assert project.owner_id is None
