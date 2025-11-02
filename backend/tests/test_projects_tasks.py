from src.task.models import TaskStatus
from src.project.models import ProjectStatus


def test_project_and_tasks_integration_flow(client, manager_user, member_user, auth_token):
    token_manager = auth_token(manager_user.email, "pass")

    resp = client.post(
        "/api/projects",
        json={"name": "Project Integration", "description": "Test integration"},
        headers={"Authorization": f"Bearer {token_manager}"},
    )
    assert resp.status_code == 201
    project_id = resp.get_json()["id"]
    assert resp.get_json()["status"] == ProjectStatus.PLANNED.value

    resp = client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": member_user.id},
        headers={"Authorization": f"Bearer {token_manager}"},
    )
    assert resp.status_code == 204

    token_member = auth_token(member_user.email, "pass")

    resp = client.post(
        "/api/tasks",
        json={"title": "Task 1", "description": "Description", "project_id": project_id, "assignee_id": member_user.id},
        headers={"Authorization": f"Bearer {token_manager}"},
    )
    assert resp.status_code == 201
    task_id = resp.get_json()["id"]
    assert resp.get_json()["status"] == TaskStatus.PENDING.value

    resp = client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": TaskStatus.IN_PROGRESS.value},
        headers={"Authorization": f"Bearer {token_member}"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == TaskStatus.IN_PROGRESS.value

    resp = client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": TaskStatus.DONE.value},
        headers={"Authorization": f"Bearer {token_member}"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {token_member}"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == ProjectStatus.COMPLETED.value
