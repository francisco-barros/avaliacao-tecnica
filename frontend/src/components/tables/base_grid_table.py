import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Callable
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import sys
import os

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class GridColumnConfig:
    def __init__(
        self,
        field: str,
        header_name: str,
        width: Optional[int] = None,
        flex: Optional[float] = None,
        hide: bool = False
    ):
        self.field = field
        self.header_name = header_name
        self.width = width
        self.flex = flex
        self.hide = hide


class GridTableConfig:
    def __init__(
        self,
        columns: List[GridColumnConfig],
        id_field: str = "id",
        height: int = 400,
        width: str = "100%",
        pre_select_first: bool = True,
        css_class: str = "ag-theme-streamlit"
    ):
        self.columns = columns
        self.id_field = id_field
        self.height = height
        self.width = width
        self.pre_select_first = pre_select_first
        self.css_class = css_class


def load_css(css_file: str) -> None:
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    css_path = os.path.join(base_path, "styles", css_file)
    
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_grid_table(
    data: List[Dict],
    config: GridTableConfig,
    css_file: Optional[str] = None,
    actions: Optional[List[Dict]] = None,
    key: str = "grid_table",
    empty_message: str = "No data found",
    data_transform: Optional[Callable[[List[Dict]], List[Dict]]] = None
) -> Optional[Dict]:
    if not data:
        st.info(empty_message)
        return None
    
    if css_file:
        load_css(css_file)
    
    transformed_data = data_transform(data) if data_transform else data
    
    df_data = []
    data_dict = {}
    
    for idx, item in enumerate(transformed_data):
        row = {}
        for col in config.columns:
            field_value = item.get(col.field, "")
            row[col.field] = str(field_value)
        df_data.append(row)
        original_id = str(item.get(config.id_field, ""))
        data_dict[original_id] = data[idx]
    
    df = pd.DataFrame(df_data)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    
    for col in config.columns:
        if col.hide:
            gb.configure_column(col.field, hide=True)
        else:
            col_config = gb.configure_column(
                col.field,
                headerName=col.header_name,
                width=col.width if col.width else None,
                flex=col.flex if col.flex else None
            )
    
    gb.configure_selection("single", use_checkbox=False)
    grid_options = gb.build()
    
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=config.height,
        width=config.width,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        enable_enterprise_modules=False,
        theme='streamlit',
        pre_selected_rows=[0] if config.pre_select_first and len(df) > 0 else [],
        key=key
    )
    
    selected_rows = grid_response.get("selected_rows")
    
    if selected_rows is not None:
        if isinstance(selected_rows, pd.DataFrame):
            if not selected_rows.empty:
                selected_rows_list = selected_rows.to_dict('records')
            else:
                selected_rows_list = []
        elif isinstance(selected_rows, list):
            selected_rows_list = selected_rows
        else:
            selected_rows_list = []
    else:
        selected_rows_list = []
    
    if selected_rows_list and len(selected_rows_list) > 0:
        selected_row = selected_rows_list[0]
        row_id = selected_row.get(config.id_field)
        selected_item = data_dict.get(row_id)
        
        if selected_item and actions:
            st.markdown("---")
            
            for action in actions:
                button_key = f"{key}_{action['key']}"
                
                if action.get("can_perform", True):
                    if st.button(
                        action["label"],
                        use_container_width=True,
                        key=button_key,
                        disabled=action.get("disabled", False)
                    ):
                        return {
                            "action": action["name"],
                            "item": selected_item
                        }
                else:
                    if st.button(
                        action["label"],
                        use_container_width=True,
                        key=button_key,
                        disabled=True
                    ):
                        pass
    else:
        if len(df_data) > 0 and actions:
            first_item = df_data[0]
            selected_item = data_dict.get(first_item[config.id_field])
            
            if selected_item:
                st.markdown("---")
                
                for action in actions:
                    button_key = f"{key}_{action['key']}"
                    
                    if st.button(
                        action["label"],
                        use_container_width=True,
                        key=button_key,
                        disabled=True
                    ):
                        pass
    
    return None

