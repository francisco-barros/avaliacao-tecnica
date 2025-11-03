import streamlit as st
import sys
import os
from typing import List, Dict, Optional

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.api.user_service import UserService
from services.api.project_service import ProjectService
from utils.helpers import show_error, show_success, show_info


def render_member_manager(project: Dict, project_service: ProjectService, user_service: UserService) -> Dict:
    st.markdown("### Manage Members")
    
    project_id = project.get("id")
    
    try:
        updated_project = project_service.get_project(project_id)
        if updated_project:
            project = updated_project
    except:
        pass
    
    current_member_ids = project.get("members", [])
    
    try:
        all_users = user_service.list_users()
        available_users = [
            user for user in all_users 
            if user.get("id") not in current_member_ids and user.get("id") != project.get("owner_id")
        ]
        
        if available_users:
            st.markdown("#### Add Member")
            user_options = {f"{user.get('name', '')} ({user.get('email', '')})": user.get("id") for user in available_users}
            
            selected_user_name = st.selectbox(
                "Select user to add",
                options=list(user_options.keys()),
                key=f"add_member_select_{project_id}"
            )
            
            if st.button("Add Member", key=f"btn_add_member_{project_id}", use_container_width=True):
                selected_user_id = user_options.get(selected_user_name)
                if selected_user_id:
                    try:
                        project_service.add_member(project_id, selected_user_id)
                        show_success("Member added successfully!")
                        st.session_state.projects_cache_cleared = True
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "403" in error_msg or "Forbidden" in error_msg:
                            show_error("You do not have permission to add members")
                        elif "404" in error_msg:
                            show_error("Project or user not found")
                        elif "completed" in error_msg.lower():
                            show_error("Cannot add members to completed projects")
                        else:
                            show_error(f"Error adding member: {error_msg}")
        else:
            st.info("No available users to add")
        
        if current_member_ids:
            st.markdown("#### Current Members")
            
            try:
                member_users = [
                    user for user in all_users 
                    if user.get("id") in current_member_ids
                ]
                
                for member in member_users:
                    col_name, col_email, col_remove = st.columns([2, 2, 1])
                    with col_name:
                        st.write(member.get("name", "Unknown"))
                    with col_email:
                        st.write(member.get("email", "Unknown"))
                    with col_remove:
                        if st.button("Remove", key=f"btn_remove_{member.get('id')}_{project_id}", use_container_width=True):
                            try:
                                project_service.remove_member(project_id, member.get("id"))
                                show_success(f"Member {member.get('name')} removed successfully!")
                                st.session_state.projects_cache_cleared = True
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "403" in error_msg or "Forbidden" in error_msg:
                                    show_error("You do not have permission to remove members")
                                elif "404" in error_msg:
                                    show_error("Project or user not found")
                                else:
                                    show_error(f"Error removing member: {error_msg}")
            except Exception as e:
                show_error(f"Error loading members: {str(e)}")
        else:
            st.info("No members in this project")
            
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            show_error("Session expired. Please login again.")
        elif "403" in error_msg or "Forbidden" in error_msg:
            show_error("You do not have permission to view users")
        else:
            show_error(f"Error loading users: {error_msg}")
    
    return project

