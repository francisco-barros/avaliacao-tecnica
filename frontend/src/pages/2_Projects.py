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
from utils.constants import UserRole, ProjectStatus
from utils.helpers import show_error, show_success, show_info
from components.forms.project_form import render_project_form
from components.tables.projects_table import render_projects_table
from components.tables.tasks_table import render_tasks_table
from components.managers.member_manager import render_member_manager

st.set_page_config(
    page_title="Projects",
    page_icon="📁",
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

def handle_project_update(project_service, selected_project, edit_data, table_action_key):
    try:
        updated_project = project_service.update_project(
            selected_project["id"],
            edit_data
        )
        show_success(f"Project {updated_project.get('name')} updated successfully!")
        if table_action_key in st.session_state:
            del st.session_state[table_action_key]
        st.session_state.projects_cache_cleared = True
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            show_error("You do not have permission to edit this project")
        elif "404" in error_msg:
            show_error("Project not found")
        elif "read-only" in error_msg.lower() or "completed" in error_msg.lower():
            show_error("Completed projects are read-only")
        else:
            show_error(f"Error updating project: {error_msg}")

def handle_project_deletion(project_service, selected_project, table_action_key, delete_modal_state_key):
    try:
        project_service.delete_project(selected_project["id"])
        show_success(f"Project {selected_project.get('name')} deleted successfully!")
        if table_action_key in st.session_state:
            del st.session_state[table_action_key]
        if delete_modal_state_key in st.session_state:
            del st.session_state[delete_modal_state_key]
        st.session_state.projects_cache_cleared = True
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            show_error("You do not have permission to delete this project")
        elif "404" in error_msg:
            show_error("Project not found")
        else:
            show_error(f"Error deleting project: {error_msg}")

def render_delete_project_modal(selected_project, table_action_key, delete_modal_state_key, project_service):
    @st.dialog("Delete Project Confirmation")
    def delete_confirmation_dialog():
        st.markdown(f"### ⚠️ Delete Project: {selected_project.get('name')}")
        st.warning(f"Are you sure you want to delete project **{selected_project.get('name')}**?\n\nThis action **cannot be undone**.")
        
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.button("Confirm Deletion", type="primary", use_container_width=True):
                handle_project_deletion(project_service, selected_project, table_action_key, delete_modal_state_key)
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                if table_action_key in st.session_state:
                    del st.session_state[table_action_key]
                if delete_modal_state_key in st.session_state:
                    del st.session_state[delete_modal_state_key]
                st.rerun()
    
    delete_confirmation_dialog()

def render_project_edit_section(project_service, selected_project, table_action_key):
    if selected_project.get("status") == ProjectStatus.COMPLETED:
        st.warning("Completed projects cannot be edited")
        return
    
    st.markdown("---")
    edit_data = render_project_form(editing_project=selected_project)
    if edit_data:
        handle_project_update(project_service, selected_project, edit_data, table_action_key)

def render_project_tasks_section(task_service, selected_project):
    st.markdown("---")
    st.markdown(f"### Tasks: {selected_project.get('name')}")
    
    try:
        tasks = task_service.list_tasks(selected_project.get("id"))
        if tasks:
            for task in tasks:
                task["project_name"] = selected_project.get("name", "Unknown")
            render_tasks_table(tasks, can_edit=False, can_reassign=False, show_project=False)
        else:
            st.info("No tasks found for this project")
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            show_error("Session expired. Please login again.")
        else:
            show_error(f"Error loading tasks: {error_msg}")

def render_project_members_section(selected_project, project_service, user_service, is_owner):
    if not is_owner:
        st.warning("Only the project owner can manage members")
        return
    
    st.markdown("---")
    updated_project = render_member_manager(selected_project, project_service, user_service)
    return updated_project if updated_project and updated_project != selected_project else selected_project

def handle_project_creation(project_service, project_data):
    try:
        new_project = project_service.create_project(project_data)
        show_success(f"Project {new_project.get('name')} created successfully!")
        st.session_state.projects_cache_cleared = True
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            show_error("You do not have permission to create projects")
        else:
            show_error(f"Error creating project: {error_msg}")

def render_create_project_section(project_service, can_create_projects):
    if not can_create_projects:
        st.warning("You do not have permission to create projects. Only Managers and Administrators can create projects.")
        return
    
    project_data = render_project_form()
    if project_data:
        handle_project_creation(project_service, project_data)

def render_project_action_section(project_service, task_service, user_service, selected_project, table_action, table_action_key, can_edit_projects, can_delete_projects, is_owner, user_id):
    if table_action["action"] == "edit" and can_edit_projects and is_owner:
        render_project_edit_section(project_service, selected_project, table_action_key)
    
    elif table_action["action"] == "delete" and can_delete_projects and is_owner:
        delete_modal_state_key = f"delete_modal_open_{selected_project['id']}"
        st.session_state[delete_modal_state_key] = True
        render_delete_project_modal(selected_project, table_action_key, delete_modal_state_key, project_service)
        if delete_modal_state_key not in st.session_state:
            st.rerun()
    
    elif table_action["action"] == "view_tasks":
        render_project_tasks_section(task_service, selected_project)
    
    elif table_action["action"] == "manage_members":
        updated_project = render_project_members_section(selected_project, project_service, user_service, is_owner)
        if updated_project != selected_project:
            table_action["item"] = updated_project

def render_projects_list_section(project_service, task_service, user_service, can_edit_projects, can_delete_projects, user_id):
    if st.session_state.get("projects_cache_cleared"):
        del st.session_state.projects_cache_cleared
        import time
        time.sleep(0.1)
    
    projects = project_service.list_projects()
    
    if not projects:
        st.info("No projects found")
        return
    
    table_action_key = "pending_project_table_action"
    if table_action_key not in st.session_state:
        st.session_state[table_action_key] = None
    
    new_table_action = render_projects_table(
        projects=projects,
        on_delete=None,
        on_edit=None,
        can_delete=can_delete_projects,
        can_edit=can_edit_projects
    )
    
    if new_table_action:
        st.session_state[table_action_key] = new_table_action
        st.rerun()
    
    table_action = st.session_state.get(table_action_key)
    if not table_action:
        return
    
    selected_project = table_action["item"]
    is_owner = selected_project.get("owner_id") == user_id
    
    render_project_action_section(
        project_service,
        task_service,
        user_service,
        selected_project,
        table_action,
        table_action_key,
        can_edit_projects,
        can_delete_projects,
        is_owner,
        user_id
    )

def render_projects_content(project_service, task_service, user_service, can_create_projects, can_edit_projects, can_delete_projects, user_id):
    tabs = st.tabs(["Projects List", "Create Project"])
    
    with tabs[0]:
        st.markdown("### Projects List")
        try:
            render_projects_list_section(
                project_service,
                task_service,
                user_service,
                can_edit_projects,
                can_delete_projects,
                user_id
            )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                show_error("Session expired. Please login again.")
                logout()
                st.rerun()
            elif "403" in error_msg or "Forbidden" in error_msg:
                show_error("You do not have permission to view projects")
            else:
                show_error(f"Error loading projects: {error_msg}")
    
    with tabs[1]:
        render_create_project_section(project_service, can_create_projects)

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

st.title("📁 Projects")

if not is_authenticated():
    st.warning("Please login to access projects")
    st.stop()

user = get_user()
user_role = get_user_role()
user_id = user.get("id") if user else None

can_create_projects = user_role in [UserRole.MANAGER, UserRole.ADMIN]
can_edit_projects = can_create_projects
can_delete_projects = can_create_projects

col_header, col_logout = st.columns([5, 1])
with col_header:
    st.markdown(f"### Welcome, {user.get('name', 'User')}")
with col_logout:
    if st.button("Logout", use_container_width=True):
        logout()
        show_info("Logout successful")
        st.rerun()

st.markdown("---")

render_projects_content(
    project_service,
    task_service,
    user_service,
    can_create_projects,
    can_edit_projects,
    can_delete_projects,
    user_id
)

