import streamlit as st
import sys
import os
from typing import Optional, Dict, Callable, List

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.validators import validate_required
from utils.helpers import show_error
from services.api.user_service import UserService

def render_task_form(projects: List[Dict], user_service: UserService, user_id: Optional[str] = None, on_submit: Optional[Callable] = None) -> Optional[Dict]:
    st.markdown("### Create New Task")
    form_key = "task_form_create"
    
    with st.form(form_key, clear_on_submit=True):
        title_key = f"{form_key}_title"
        description_key = f"{form_key}_description"
        project_key = f"{form_key}_project"
        assignee_key = f"{form_key}_assignee"
        
        title = st.text_input(
            "Title",
            value="",
            key=title_key
        )
        
        description = st.text_area(
            "Description",
            value="",
            key=description_key,
            height=100
        )
        
        if not projects:
            st.warning("No available projects. You need to be a member or owner of at least one project.")
            return None
        
        project_options = {f"{p.get('name', 'Unknown')}": p.get("id") for p in projects if p.get("status") != "completed"}
        
        if not project_options:
            st.warning("No available projects. Completed projects cannot receive new tasks.")
            return None
        
        selected_project_name = st.selectbox(
            "Project",
            options=list(project_options.keys()),
            key=project_key
        )
        
        selected_project_id = project_options.get(selected_project_name)
        selected_project = next((p for p in projects if p.get("id") == selected_project_id), None)
        
        assignee_options = ["Unassigned"]
        assignee_ids = {"Unassigned": None}
        
        if selected_project:
            try:
                all_users = user_service.list_users()
                users_dict = {u.get("id"): u for u in all_users}
                
                project_members = selected_project.get("members", [])
                owner_id = selected_project.get("owner_id")
                
                if owner_id and owner_id in users_dict:
                    owner = users_dict[owner_id]
                    assignee_options.append(f"{owner.get('name', 'Unknown')} (Owner)")
                    assignee_ids[f"{owner.get('name', 'Unknown')} (Owner)"] = owner_id
                
                for member_id in project_members:
                    if member_id in users_dict:
                        member = users_dict[member_id]
                        assignee_options.append(f"{member.get('name', 'Unknown')} ({member.get('email', 'Unknown')})")
                        assignee_ids[f"{member.get('name', 'Unknown')} ({member.get('email', 'Unknown')})"] = member_id
            except:
                pass
        
        selected_assignee_name = st.selectbox(
            "Assignee",
            options=assignee_options,
            key=assignee_key
        )
        
        selected_assignee_id = assignee_ids.get(selected_assignee_name)
        
        submit_button = st.form_submit_button("Create", use_container_width=True)
        
        if submit_button:
            if not validate_required(title):
                show_error("Title is required")
                return None
            
            if not validate_required(description):
                show_error("Description is required")
                return None
            
            if not selected_project_id:
                show_error("Project is required")
                return None
            
            data = {
                "title": title,
                "description": description,
                "project_id": selected_project_id
            }
            
            if selected_assignee_id:
                data["assignee_id"] = selected_assignee_id
            
            return data
    
    return None

