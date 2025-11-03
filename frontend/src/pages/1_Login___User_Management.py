import streamlit as st
import sys
import os

src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services import AuthService, UserService
from state.auth_state import (
    is_authenticated,
    logout,
    get_user,
    get_user_role,
    get_token,
    set_token,
    set_refresh_token,
    set_user
)
from utils.constants import UserRole
from utils.helpers import show_error, show_success, show_info
from utils.formatters import format_role
from components.forms.login_form import render_login_form
from components.forms.user_form import render_user_form
from components.tables.users_table import render_users_table

st.set_page_config(
    page_title="Login / User Management",
    page_icon="🔐",
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

if "auth_service" not in st.session_state:
    st.session_state.auth_service = AuthService()

if "user_service" not in st.session_state:
    st.session_state.user_service = UserService()

auth_service = st.session_state.auth_service
user_service = st.session_state.user_service

st.title("🔐 Login / User Management")

token = get_token()
user = get_user()

if token and user:
    if not is_authenticated():
        set_user(user)
        set_token(token)

if not is_authenticated():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        login_data = render_login_form()
        
        if login_data:
            try:
                response = auth_service.login(login_data["email"], login_data["password"])
                
                access_token = None
                refresh_token = None
                user_id = None
                
                access_token = response.get("access_token")
                refresh_token = response.get("refresh_token")
                
                if access_token and refresh_token:
                    try:
                        import base64
                        import json
                        
                        token_parts = access_token.split('.')
                        if len(token_parts) >= 2:
                            payload_part = token_parts[1]
                            padding = len(payload_part) % 4
                            if padding:
                                payload_part += '=' * (4 - padding)
                            
                            payload = json.loads(base64.urlsafe_b64decode(payload_part))
                            user_id_from_token = payload.get("sub")
                            
                            if user_id_from_token:
                                logged_user = user_service.get_user(user_id_from_token)
                                if logged_user and isinstance(logged_user, dict):
                                    set_token(access_token)
                                    set_refresh_token(refresh_token)
                                    set_user(logged_user)
                                    show_success(f"Welcome, {logged_user.get('name', 'User')}!")
                                    st.rerun()
                                else:
                                    raise Exception("User data not found")
                            else:
                                raise Exception("User ID not found in token")
                        else:
                            raise Exception("Invalid token format")
                    except Exception as e:
                        error_msg = str(e)
                        try:
                            set_token(access_token)
                            set_refresh_token(refresh_token)
                            
                            user_response = user_service.list_users()
                            if isinstance(user_response, list) and len(user_response) > 0:
                                logged_user = next(
                                    (u for u in user_response if u.get("email") == login_data["email"]),
                                    None
                                )
                                if logged_user:
                                    set_user(logged_user)
                                    show_success(f"Welcome, {logged_user.get('name', 'User')}!")
                                    st.rerun()
                        except Exception as fallback_error:
                            set_token(access_token)
                            set_refresh_token(refresh_token)
                            fallback_msg = str(fallback_error)
                            if "403" in fallback_msg or "Forbidden" in fallback_msg:
                                show_error("You don't have permission to list users. Contact an administrator.")
                            elif "401" in fallback_msg:
                                show_error("Authentication failed. Please try again.")
                            else:
                                show_error(f"Error loading user data: {fallback_msg}")
                        
                        if "401" in error_msg or "Unauthorized" in error_msg:
                            show_error("Session expired. Please login again.")
                        elif "403" in error_msg or "Forbidden" in error_msg:
                            show_error("You don't have permission to access user data.")
                        elif "User data not found" not in error_msg and "User ID not found" not in error_msg:
                            show_error(f"Error loading user data: {error_msg}")
                else:
                    show_error("Invalid server response")
                    
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "Unauthorized" in error_msg:
                    show_error("Invalid credentials")
                else:
                    show_error(f"Login error: {error_msg}")
    
    with col2:
        st.markdown("### Test Credentials (Seed)")
        st.markdown("""
        **Administrator:**
        - Email: `admin@example.com`
        - Password: `admin123`
        
        **Manager:**
        - Email: `manager1@example.com`
        - Password: `manager123`
        
        **Member:**
        - Email: `member1@example.com`
        - Password: `member123`
        """)

else:
    user = get_user()
    user_role = get_user_role()
    
    can_manage_users = user_role in [UserRole.ADMIN, UserRole.MANAGER]
    can_register_users = can_manage_users
    can_delete_users = user_role == UserRole.ADMIN
    can_edit_users = user_role == UserRole.ADMIN
    
    col_header, col_logout = st.columns([5, 1])
    with col_header:
        st.markdown(f"### Welcome, {user.get('name', 'User')} ({format_role(user_role)})")
    with col_logout:
        if st.button("Logout", use_container_width=True):
            logout()
            show_info("Logout successful")
            st.rerun()
    
    st.markdown("---")
    
    tabs = st.tabs(["Login", "Manage Users"])
    
    with tabs[0]:
        st.markdown("### Change User")
        st.info("You are already authenticated. Logout to sign in with another account.")
    
    with tabs[1]:
        if not can_manage_users:
            st.warning("You do not have permission to manage users. Only Administrators and Managers can access this functionality.")
        else:
            col_create, col_list = st.columns([1, 2])
            
            with col_create:
                if can_register_users:
                    st.markdown("#### Register User")
                    with st.container():
                        user_data = render_user_form()
                    
                    if user_data:
                        try:
                            new_user = auth_service.register(
                                name=user_data["name"],
                                email=user_data["email"],
                                password=user_data["password"],
                                role=user_data.get("role")
                            )
                            show_success(f"User {new_user.get('name')} registered successfully!")
                            st.session_state.users_cache_cleared = True
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "403" in error_msg or "Forbidden" in error_msg:
                                show_error("You do not have permission to register users")
                            elif "409" in error_msg or "Conflict" in error_msg or "already in use" in error_msg.lower():
                                show_error("Email already in use")
                            elif "500" in error_msg:
                                if "already in use" in error_msg.lower() or "duplicate" in error_msg.lower():
                                    show_error("Email already in use")
                                else:
                                    show_error(f"Server error: {error_msg}")
                            else:
                                show_error(f"Error registering user: {error_msg}")
                else:
                    st.info("Only Administrators and Managers can register users.")
            
            with col_list:
                st.markdown("#### User List")
                try:
                    if st.session_state.get("users_cache_cleared"):
                        del st.session_state.users_cache_cleared
                        import time
                        time.sleep(0.1)
                    users = user_service.list_users()
                    
                    if users:
                        table_action_key = "pending_user_table_action"
                        if table_action_key not in st.session_state:
                            st.session_state[table_action_key] = None
                        
                        new_table_action = render_users_table(
                            users=users,
                            on_delete=None,
                            on_edit=None,
                            can_delete=can_delete_users,
                            can_edit=can_edit_users
                        )
                        
                        if new_table_action:
                            st.session_state[table_action_key] = new_table_action
                            st.rerun()
                        
                        table_action = st.session_state.get(table_action_key)
                        
                        if table_action:
                            if table_action["action"] == "edit" and can_edit_users:
                                selected_user = table_action["item"]
                                
                                st.markdown("---")
                                edit_data = render_user_form(editing_user=selected_user)
                                
                                if edit_data:
                                    try:
                                        updated_user = user_service.update_user(
                                            selected_user["id"],
                                            edit_data
                                        )
                                        show_success(f"User {updated_user.get('name')} updated successfully!")
                                        if table_action_key in st.session_state:
                                            del st.session_state[table_action_key]
                                        st.rerun()
                                    except Exception as e:
                                        error_msg = str(e)
                                        if "403" in error_msg or "Forbidden" in error_msg:
                                            show_error("You do not have permission to edit users")
                                        elif "404" in error_msg:
                                            show_error("User not found")
                                        else:
                                            show_error(f"Error updating user: {error_msg}")
                            
                            elif table_action["action"] == "delete" and can_delete_users:
                                selected_user = table_action["item"]
                                
                                delete_modal_state_key = f"delete_modal_open_{selected_user['id']}"
                                st.session_state[delete_modal_state_key] = True
                                
                                if st.session_state.get(delete_modal_state_key):
                                    @st.dialog("Delete User Confirmation")
                                    def delete_confirmation_dialog():
                                        st.markdown(f"### ⚠️ Delete User: {selected_user.get('name')}")
                                        st.warning(f"Are you sure you want to delete user **{selected_user.get('name')}** ({selected_user.get('email')})?\n\nThis action **cannot be undone**.")
                                        
                                        col_confirm, col_cancel = st.columns(2)
                                        
                                        with col_confirm:
                                            if st.button("Confirm Deletion", type="primary", use_container_width=True):
                                                try:
                                                    user_service.delete_user(selected_user["id"])
                                                    show_success(f"User {selected_user.get('name')} deleted successfully!")
                                                    if table_action_key in st.session_state:
                                                        del st.session_state[table_action_key]
                                                    if delete_modal_state_key in st.session_state:
                                                        del st.session_state[delete_modal_state_key]
                                                    st.session_state.users_cache_cleared = True
                                                    st.rerun()
                                                except Exception as e:
                                                    error_msg = str(e)
                                                    if "403" in error_msg:
                                                        show_error("You do not have permission to delete users")
                                                    elif "404" in error_msg:
                                                        show_error("User not found")
                                                    else:
                                                        show_error(f"Error deleting user: {error_msg}")
                                        
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
                    else:
                        st.info("No users found")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "401" in error_msg or "Unauthorized" in error_msg:
                        show_error("Session expired. Please login again.")
                        logout()
                        st.rerun()
                    elif "403" in error_msg or "Forbidden" in error_msg:
                        show_error("You do not have permission to view users")
                    else:
                        show_error(f"Error loading users: {error_msg}")
