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


def render_tasks_table(
    tasks: List[Dict],
    can_edit: bool = False
) -> Optional[Dict]:
    columns = [
        GridColumnConfig(field="id", header_name="ID", hide=True),
        GridColumnConfig(field="title", header_name="Title", flex=1.5),
        GridColumnConfig(field="description", header_name="Description", flex=2),
        GridColumnConfig(field="status", header_name="Status", flex=1),
        GridColumnConfig(field="assignee_id", header_name="Assignee ID", hide=True),
    ]
    
    config = GridTableConfig(
        columns=columns,
        id_field="id",
        height=300,
        width="100%",
        pre_select_first=False,
        css_class="ag-theme-streamlit"
    )
    
    def transform_tasks(tasks_list):
        return [
            {
                "id": str(task.get("id", "")),
                "title": task.get("title", ""),
                "description": task.get("description", "")[:100] + "..." if len(task.get("description", "")) > 100 else task.get("description", ""),
                "status": format_status(task.get("status", "")),
                "assignee_id": str(task.get("assignee_id", "")) if task.get("assignee_id") else "Unassigned",
            }
            for task in tasks_list
        ]
    
    actions = []
    
    if can_edit:
        actions.append({
            "name": "edit_status",
            "label": "Update Status",
            "key": "btn_edit_task_status",
            "can_perform": True,
            "disabled": False
        })
    
    return render_grid_table(
        data=tasks,
        config=config,
        css_file="users_table.css",
        actions=actions if actions else None,
        key="tasks_grid",
        empty_message="No tasks found",
        data_transform=transform_tasks
    )

