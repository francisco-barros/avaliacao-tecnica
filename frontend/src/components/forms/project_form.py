import streamlit as st
import sys
import os
from typing import Optional, Dict, Callable

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.validators import validate_required
from utils.helpers import show_error
from utils.constants import ProjectStatus

def render_project_form(editing_project: Optional[Dict] = None, on_submit: Optional[Callable] = None) -> Optional[Dict]:
    is_edit = editing_project is not None
    
    if is_edit:
        st.markdown("### Edit Project")
        form_key = f"project_form_edit_{editing_project.get('id', '')}"
    else:
        st.markdown("### Create New Project")
        form_key = "project_form_create"
    
    with st.form(form_key, clear_on_submit=not is_edit):
        name_key = f"{form_key}_name"
        description_key = f"{form_key}_description"
        status_key = f"{form_key}_status"
        
        name = st.text_input(
            "Name",
            value=editing_project.get("name", "") if is_edit else "",
            key=name_key
        )
        
        description = st.text_area(
            "Description",
            value=editing_project.get("description", "") if is_edit else "",
            key=description_key,
            height=100
        )
        
        status_options = [ProjectStatus.PLANNED, ProjectStatus.IN_PROGRESS, ProjectStatus.COMPLETED]
        
        if is_edit:
            project_status = editing_project.get("status", ProjectStatus.PLANNED)
            if isinstance(project_status, str):
                project_status = project_status.lower()
            try:
                status_index = status_options.index(project_status)
            except ValueError:
                status_index = status_options.index(ProjectStatus.PLANNED)
        else:
            status_index = status_options.index(ProjectStatus.PLANNED)
        
        status = st.selectbox(
            "Status",
            status_options,
            index=status_index,
            key=status_key,
            format_func=lambda x: {
                ProjectStatus.PLANNED: "Planned",
                ProjectStatus.IN_PROGRESS: "In Progress",
                ProjectStatus.COMPLETED: "Completed"
            }.get(x, x),
            disabled=is_edit and editing_project.get("status") == ProjectStatus.COMPLETED
        )
        
        submit_label = "Update" if is_edit else "Create"
        submit_button = st.form_submit_button(submit_label, use_container_width=True)
        
        if submit_button:
            if not validate_required(name):
                show_error("Name is required")
                return None
            
            if not validate_required(description):
                show_error("Description is required")
                return None
            
            data = {"name": name, "description": description}
            if is_edit:
                data["status"] = status
            
            return data
    
    return None

