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
from utils.formatters import format_role


def render_users_table(
    users: List[Dict],
    on_delete: Optional[callable] = None,
    on_edit: Optional[callable] = None,
    can_delete: bool = True,
    can_edit: bool = True
) -> Optional[Dict]:
    columns = [
        GridColumnConfig(field="id", header_name="ID", hide=True),
        GridColumnConfig(field="name", header_name="Name", flex=1),
        GridColumnConfig(field="email", header_name="Email", flex=1),
        GridColumnConfig(field="role", header_name="Role", flex=0.5),
    ]
    
    config = GridTableConfig(
        columns=columns,
        id_field="id",
        height=400,
        width="100%",
        pre_select_first=True,
        css_class="ag-theme-streamlit"
    )
    
    def transform_users(users_list):
        return [
            {
                "id": str(user.get("id", "")),
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "role": format_role(user.get("role", "")),
            }
            for user in users_list
        ]
    
    actions = []
    
    if can_edit:
        actions.append({
            "name": "edit",
            "label": "Edit User",
            "key": "btn_edit_user",
            "can_perform": True,
            "disabled": False
        })
    
    if can_delete:
        actions.append({
            "name": "delete",
            "label": "Delete User",
            "key": "btn_delete_user",
            "can_perform": True,
            "disabled": False
        })
    
    return render_grid_table(
        data=users,
        config=config,
        css_file="users_table.css",
        actions=actions if actions else None,
        key="users_grid",
        empty_message="No users found",
        data_transform=transform_users
    )

