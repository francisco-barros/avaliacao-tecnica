def format_status(status):
    status_map = {
        "planned": "Planned",
        "in_progress": "In Progress",
        "completed": "Completed",
        "pending": "Pending",
        "done": "Done",
        "awaiting_reassignment": "Awaiting Reassignment",
    }
    return status_map.get(status, status)

def format_role(role):
    role_map = {
        "admin": "Admin",
        "manager": "Manager",
        "member": "Member",
    }
    return role_map.get(role, role)

