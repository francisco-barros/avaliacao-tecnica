import streamlit as st
import sys
import os
from typing import List, Dict, Optional

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from components.tables.base_grid_table import (
    render_grid_table,
    GridTableConfig,
    GridColumnConfig
)
from utils.formatters import format_status


def render_projects_table(
    projects: List[Dict],
    on_delete: Optional[callable] = None,
    on_edit: Optional[callable] = None,
    can_delete: bool = True,
    can_edit: bool = True
) -> Optional[Dict]:
    columns = [
        GridColumnConfig(field="id", header_name="ID", hide=True),
        GridColumnConfig(field="name", header_name="Name", flex=1.5),
        GridColumnConfig(field="description", header_name="Description", flex=2),
        GridColumnConfig(field="status", header_name="Status", flex=0.8),
        GridColumnConfig(field="owner_id", header_name="Owner ID", hide=True),
    ]
    
    config = GridTableConfig(
        columns=columns,
        id_field="id",
        height=400,
        width="100%",
        pre_select_first=True,
        css_class="ag-theme-streamlit"
    )
    
    def transform_projects(projects_list):
        return [
            {
                "id": str(project.get("id", "")),
                "name": project.get("name", ""),
                "description": project.get("description", "")[:100] + "..." if len(project.get("description", "")) > 100 else project.get("description", ""),
                "status": format_status(project.get("status", "")),
                "owner_id": str(project.get("owner_id", "")),
            }
            for project in projects_list
        ]
    
    actions = []
    
    if can_edit:
        actions.append({
            "name": "edit",
            "label": "Edit Project",
            "key": "btn_edit_project",
            "can_perform": True,
            "disabled": False
        })
    
    if can_delete:
        actions.append({
            "name": "delete",
            "label": "Delete Project",
            "key": "btn_delete_project",
            "can_perform": True,
            "disabled": False
        })
    
    actions.append({
        "name": "view_tasks",
        "label": "View Tasks",
        "key": "btn_view_tasks",
        "can_perform": True,
        "disabled": False
    })
    
    if can_edit:
        actions.append({
            "name": "manage_members",
            "label": "Manage Members",
            "key": "btn_manage_members",
            "can_perform": True,
            "disabled": False
        })
    
    return render_grid_table(
        data=projects,
        config=config,
        css_file="users_table.css",
        actions=actions if actions else None,
        key="projects_grid",
        empty_message="No projects found",
        data_transform=transform_projects
    )

