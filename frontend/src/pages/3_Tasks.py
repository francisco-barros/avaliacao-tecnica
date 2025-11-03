import streamlit as st
import sys
import os

src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services import ProjectService, TaskService, UserService
from state.auth_state import (
    is_authenticated,
    get_user,
    get_user_role,
    logout
)
from utils.constants import UserRole, TaskStatus
from utils.helpers import show_error, show_success, show_info
from components.forms.task_form import render_task_form
from components.tables.tasks_table import render_tasks_table

st.set_page_config(
    page_title="Tasks",
    page_icon="✅",
    layout="wide"
)

def load_css():
    import os
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main_css = os.path.join(base_path, "styles", "main.css")
    components_css = os.path.join(base_path, "styles", "components.css")
    
    if os.path.exists(main_css):
        with open(main_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    if os.path.exists(components_css):
        with open(components_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_all_tasks(project_service, task_service):
    projects = project_service.list_projects()
    all_tasks = []
    
    for project in projects:
        try:
            project_tasks = task_service.list_tasks(project.get("id"))
            for task in project_tasks:
                task["project_name"] = project.get("name", "Unknown")
                all_tasks.append(task)
        except:
            pass
    
    return all_tasks

def can_update_task_status(selected_task, user_id):
    task_assignee_id = selected_task.get("assignee_id")
    return task_assignee_id == user_id or str(task_assignee_id) == str(user_id)

def get_current_status_index(current_status, task_status_options):
    try:
        return task_status_options.index(current_status.lower())
    except ValueError:
        return 0

def handle_task_status_update(task_service, selected_task, new_status, table_action_key):
    try:
        task_service.update_status(selected_task.get("id"), new_status)
        show_success("Task status updated successfully!")
        if table_action_key in st.session_state:
            del st.session_state[table_action_key]
        st.session_state.tasks_cache_cleared = True
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            show_error("You do not have permission to update this task. Only the task assignee can update the status.")
        elif "404" in error_msg:
            show_error("Task not found")
        else:
            show_error(f"Error updating task: {error_msg}")

def render_status_update_form(task_service, selected_task, user_id, table_action_key):
    if not can_update_task_status(selected_task, user_id):
        task_assignee_id = selected_task.get("assignee_id")
        if task_assignee_id is None or str(task_assignee_id) == "None":
            st.warning("This task has no assignee and cannot be updated. Tasks awaiting reassignment need to be reassigned first.")
        else:
            st.warning("Only the task assignee can update the task status")
        return
    
    st.markdown("---")
    st.markdown(f"### Update Task Status: {selected_task.get('title')}")
    
    current_status = selected_task.get("status", "").lower()
    task_status_options = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
    current_index = get_current_status_index(current_status, task_status_options)
    
    new_status = st.selectbox(
        "New Status",
        task_status_options,
        index=current_index,
        key=f"task_status_{selected_task.get('id')}",
        format_func=lambda x: {
            TaskStatus.PENDING: "Pending",
            TaskStatus.IN_PROGRESS: "In Progress",
            TaskStatus.DONE: "Done"
        }.get(x, x)
    )
    
    if st.button("Update Status", key=f"btn_update_task_{selected_task.get('id')}", use_container_width=True):
        handle_task_status_update(task_service, selected_task, new_status, table_action_key)

def can_reassign_task(project_data, user_id, user_role):
    if not project_data:
        return False
    is_project_owner = project_data.get("owner_id") == user_id
    return user_role in [UserRole.ADMIN, UserRole.MANAGER] or is_project_owner

def build_assignee_options(project_data, all_users, current_assignee_id):
    assignee_options = ["Unassigned"]
    assignee_ids = {"Unassigned": None}
    
    owner_id = project_data.get("owner_id") if project_data else None
    if owner_id:
        owner = next((u for u in all_users if u.get("id") == owner_id), None)
        if owner:
            assignee_options.append(f"{owner.get('name', 'Unknown')} (Owner)")
            assignee_ids[f"{owner.get('name', 'Unknown')} (Owner)"] = owner_id
    
    project_member_ids = project_data.get("members", []) if project_data else []
    for member_id in project_member_ids:
        member = next((u for u in all_users if u.get("id") == member_id), None)
        if member:
            display_name = f"{member.get('name', 'Unknown')} ({member.get('email', 'Unknown')})"
            assignee_options.append(display_name)
            assignee_ids[display_name] = member_id
    
    if current_assignee_id and current_assignee_id != "Unassigned":
        current_user = next((u for u in all_users if u.get("id") == current_assignee_id), None)
        if current_user:
            current_display = f"{current_user.get('name', 'Unknown')} ({current_user.get('email', 'Unknown')})"
            if current_display not in assignee_options:
                assignee_options.insert(1, current_display)
                assignee_ids[current_display] = current_assignee_id
    
    return assignee_options, assignee_ids

def get_current_assignee_selection(assignee_options, current_assignee_id, all_users):
    if not current_assignee_id or current_assignee_id == "Unassigned":
        return "Unassigned"
    
    current_user = next((u for u in all_users if u.get("id") == current_assignee_id), None)
    if current_user:
        return f"{current_user.get('name', 'Unknown')} ({current_user.get('email', 'Unknown')})"
    
    return "Unassigned"

def handle_task_reassign(task_service, task_item, new_assignee_id, table_action_key):
    try:
        task_service.reassign_task(task_item.get("id"), new_assignee_id)
        show_success("Task reassigned successfully!")
        if table_action_key in st.session_state:
            del st.session_state[table_action_key]
        st.session_state.tasks_cache_cleared = True
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            show_error("You do not have permission to reassign this task. Only admin, manager or project owner can reassign tasks.")
        elif "404" in error_msg:
            show_error("Task or project not found")
        elif "must be a project member" in error_msg.lower():
            show_error("The selected assignee must be a project member or owner")
        else:
            show_error(f"Error reassigning task: {error_msg}")

def render_reassign_form(task_service, project_service, user_service, task_item, user_id, user_role, table_action_key):
    st.markdown("---")
    st.markdown(f"### Reassign Task: {task_item.get('title')}")
    
    task_project_id = task_item.get("project_id")
    
    try:
        project_data = project_service.get_project(task_project_id)
        
        if not can_reassign_task(project_data, user_id, user_role):
            st.warning("Only admin, manager or project owner can reassign tasks")
            return
        
        all_users = user_service.list_users()
        assignee_options, assignee_ids = build_assignee_options(project_data, all_users, task_item.get("assignee_id"))
        
        current_selected = get_current_assignee_selection(assignee_options, task_item.get("assignee_id"), all_users)
        
        try:
            current_index = assignee_options.index(current_selected)
        except ValueError:
            current_index = 0
        
        new_assignee_name = st.selectbox(
            "New Assignee",
            options=assignee_options,
            index=current_index,
            key=f"reassign_assignee_{task_item.get('id')}"
        )
        
        new_assignee_id = assignee_ids.get(new_assignee_name)
        
        if st.button("Reassign Task", key=f"btn_reassign_{task_item.get('id')}", use_container_width=True):
            handle_task_reassign(task_service, task_item, new_assignee_id, table_action_key)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            show_error("Session expired. Please login again.")
        else:
            show_error(f"Error loading project data: {error_msg}")

def render_tasks_list_section(project_service, task_service, user_service, user_id, user_role):
    if st.session_state.get("tasks_cache_cleared"):
        del st.session_state.tasks_cache_cleared
        import time
        time.sleep(0.1)
    
    all_tasks = load_all_tasks(project_service, task_service)
    
    if not all_tasks:
        st.info("No tasks found")
        return
    
    table_action_key = "pending_task_table_action"
    if table_action_key not in st.session_state:
        st.session_state[table_action_key] = None
    
    can_edit_task_status = True
    can_reassign_tasks = user_role in [UserRole.ADMIN, UserRole.MANAGER]
    
    new_table_action = render_tasks_table(
        tasks=all_tasks,
        can_edit=can_edit_task_status,
        can_reassign=can_reassign_tasks,
        show_project=True
    )
    
    if new_table_action:
        st.session_state[table_action_key] = new_table_action
        st.rerun()
    
    table_action = st.session_state.get(table_action_key)
    if not table_action:
        return
    
    selected_task = table_action["item"]
    
    if table_action["action"] == "edit_status":
        render_status_update_form(task_service, selected_task, user_id, table_action_key)
    elif table_action.get("action") == "reassign":
        render_reassign_form(task_service, project_service, user_service, selected_task, user_id, user_role, table_action_key)

def handle_task_creation(task_service, task_data):
    try:
        new_task = task_service.create_task(task_data)
        show_success(f"Task {new_task.get('title')} created successfully!")
        st.session_state.tasks_cache_cleared = True
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            show_error("You do not have permission to create tasks")
        elif "404" in error_msg or "not found" in error_msg.lower():
            show_error("Project not found or you don't have access to it")
        elif "completed" in error_msg.lower():
            show_error("Cannot add tasks to completed projects")
        else:
            show_error(f"Error creating task: {error_msg}")

def get_available_projects(projects, user_id):
    return [
        p for p in projects 
        if p.get("status") != "completed" and (
            p.get("owner_id") == user_id or 
            user_id in p.get("members", [])
        )
    ]

def render_create_task_section(project_service, task_service, user_service, user_id):
    try:
        projects = project_service.list_projects()
        available_projects = get_available_projects(projects, user_id)
        
        if not available_projects:
            st.warning("You need to be a member or owner of at least one active project to create tasks.")
            return
        
        task_data = render_task_form(projects=available_projects, user_service=user_service, user_id=user_id)
        if task_data:
            handle_task_creation(task_service, task_data)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            show_error("Session expired. Please login again.")
        else:
            show_error(f"Error loading projects: {error_msg}")

def handle_tasks_list_error(error_msg, logout_func):
    if "401" in error_msg or "Unauthorized" in error_msg:
        show_error("Session expired. Please login again.")
        logout_func()
        st.rerun()
    elif "403" in error_msg or "Forbidden" in error_msg:
        show_error("You do not have permission to view tasks")
    else:
        show_error(f"Error loading tasks: {error_msg}")

load_css()

if "project_service" not in st.session_state:
    st.session_state.project_service = ProjectService()

if "task_service" not in st.session_state:
    st.session_state.task_service = TaskService()

if "user_service" not in st.session_state:
    st.session_state.user_service = UserService()

project_service = st.session_state.project_service
task_service = st.session_state.task_service
user_service = st.session_state.user_service

st.title("✅ Tasks")

if not is_authenticated():
    st.warning("Please login to access tasks")
    st.stop()

user = get_user()
user_role = get_user_role()
user_id = user.get("id") if user else None

col_header, col_logout = st.columns([5, 1])
with col_header:
    st.markdown(f"### Welcome, {user.get('name', 'User')}")
with col_logout:
    if st.button("Logout", use_container_width=True):
        logout()
        show_info("Logout successful")
        st.rerun()

st.markdown("---")

tabs = st.tabs(["Tasks List", "Create Task"])

with tabs[0]:
    st.markdown("### Tasks List")
    try:
        render_tasks_list_section(project_service, task_service, user_service, user_id, user_role)
    except Exception as e:
        handle_tasks_list_error(str(e), logout)

with tabs[1]:
    render_create_task_section(project_service, task_service, user_service, user_id)
