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
from utils.constants import UserRole, ProjectStatus, TaskStatus
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

tabs = st.tabs(["Projects List", "Create Project"])

with tabs[0]:
    st.markdown("### Projects List")
    
    try:
        if st.session_state.get("projects_cache_cleared"):
            del st.session_state.projects_cache_cleared
            import time
            time.sleep(0.1)
        
        projects = project_service.list_projects()
        
        if projects:
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
            
            if table_action:
                selected_project = table_action["item"]
                is_owner = selected_project.get("owner_id") == user_id
                
                if table_action["action"] == "edit" and can_edit_projects and is_owner:
                    if selected_project.get("status") == ProjectStatus.COMPLETED:
                        st.warning("Completed projects cannot be edited")
                    else:
                        st.markdown("---")
                        edit_data = render_project_form(editing_project=selected_project)
                        
                        if edit_data:
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
                
                elif table_action["action"] == "delete" and can_delete_projects and is_owner:
                    delete_modal_state_key = f"delete_modal_open_{selected_project['id']}"
                    st.session_state[delete_modal_state_key] = True
                    
                    if st.session_state.get(delete_modal_state_key):
                        @st.dialog("Delete Project Confirmation")
                        def delete_confirmation_dialog():
                            st.markdown(f"### ⚠️ Delete Project: {selected_project.get('name')}")
                            st.warning(f"Are you sure you want to delete project **{selected_project.get('name')}**?\n\nThis action **cannot be undone**.")
                            
                            col_confirm, col_cancel = st.columns(2)
                            
                            with col_confirm:
                                if st.button("Confirm Deletion", type="primary", use_container_width=True):
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
                            
                            with col_cancel:
                                if st.button("Cancel", use_container_width=True):
                                    if table_action_key in st.session_state:
                                        del st.session_state[table_action_key]
                                    if delete_modal_state_key in st.session_state:
                                        del st.session_state[delete_modal_state_key]
                                    st.rerun()
                        
                        delete_confirmation_dialog()
                        
                        if delete_modal_state_key not in st.session_state:
                            st.rerun()
                
                elif table_action["action"] == "view_tasks":
                    st.markdown("---")
                    st.markdown(f"### Tasks: {selected_project.get('name')}")
                    
                    try:
                        tasks = task_service.list_tasks(selected_project.get("id"))
                        if tasks:
                            tasks_action = render_tasks_table(tasks, can_edit=True)
                            
                            if tasks_action and tasks_action.get("action") == "edit_status":
                                task_item = tasks_action.get("item")
                                st.markdown("---")
                                st.markdown(f"### Update Task Status: {task_item.get('title')}")
                                
                                current_status = task_item.get("status", "").lower()
                                task_status_options = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
                                
                                try:
                                    current_index = task_status_options.index(current_status)
                                except ValueError:
                                    current_index = 0
                                
                                new_status = st.selectbox(
                                    "New Status",
                                    task_status_options,
                                    index=current_index,
                                    key=f"task_status_{task_item.get('id')}",
                                    format_func=lambda x: {
                                        TaskStatus.PENDING: "Pending",
                                        TaskStatus.IN_PROGRESS: "In Progress",
                                        TaskStatus.DONE: "Done"
                                    }.get(x, x)
                                )
                                
                                if st.button("Update Status", key=f"btn_update_task_{task_item.get('id')}", use_container_width=True):
                                    try:
                                        updated_task = task_service.update_status(task_item.get("id"), new_status)
                                        show_success(f"Task status updated successfully!")
                                        if table_action_key in st.session_state:
                                            del st.session_state[table_action_key]
                                        st.rerun()
                                    except Exception as e:
                                        error_msg = str(e)
                                        if "403" in error_msg:
                                            show_error("You do not have permission to update this task. Only the task assignee can update the status.")
                                        elif "404" in error_msg:
                                            show_error("Task not found")
                                        else:
                                            show_error(f"Error updating task: {error_msg}")
                        else:
                            st.info("No tasks found for this project")
                    except Exception as e:
                        error_msg = str(e)
                        if "401" in error_msg:
                            show_error("Session expired. Please login again.")
                        else:
                            show_error(f"Error loading tasks: {error_msg}")
                
                elif table_action["action"] == "manage_members":
                    if not is_owner:
                        st.warning("Only the project owner can manage members")
                    else:
                        st.markdown("---")
                        updated_project = render_member_manager(selected_project, project_service, user_service)
                        if updated_project and updated_project != selected_project:
                            selected_project = updated_project
                            table_action["item"] = updated_project
        else:
            st.info("No projects found")
            
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
    if not can_create_projects:
        st.warning("You do not have permission to create projects. Only Managers and Administrators can create projects.")
    else:
        project_data = render_project_form()
        
        if project_data:
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

