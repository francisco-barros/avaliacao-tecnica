from .settings import API_BASE_URL

API_ENDPOINTS = {
    "auth": {
        "login": f"{API_BASE_URL}/api/auth/login",
        "refresh": f"{API_BASE_URL}/api/auth/refresh",
        "register": f"{API_BASE_URL}/api/auth/register",
    },
    "users": {
        "list": f"{API_BASE_URL}/api/users",
        "get": f"{API_BASE_URL}/api/users",
        "update": f"{API_BASE_URL}/api/users",
        "delete": f"{API_BASE_URL}/api/users",
    },
    "projects": {
        "list": f"{API_BASE_URL}/api/projects",
        "get": f"{API_BASE_URL}/api/projects",
        "create": f"{API_BASE_URL}/api/projects",
        "update": f"{API_BASE_URL}/api/projects",
        "delete": f"{API_BASE_URL}/api/projects",
        "add_member": f"{API_BASE_URL}/api/projects",
        "remove_member": f"{API_BASE_URL}/api/projects",
    },
    "tasks": {
        "create": f"{API_BASE_URL}/api/tasks",
        "list": f"{API_BASE_URL}/api/tasks/project",
        "update_status": f"{API_BASE_URL}/api/tasks",
    },
}

