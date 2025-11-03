import streamlit as st
import sys
import os
import base64
import json

src_path = os.path.dirname(os.path.abspath(__file__))
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
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    main_css = os.path.join(base_path, "styles", "main.css")
    components_css = os.path.join(base_path, "styles", "components.css")
    
    if os.path.exists(main_css):
        with open(main_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    if os.path.exists(components_css):
        with open(components_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_user_id_from_token(access_token):
    try:
        token_parts = access_token.split('.')
        if len(token_parts) < 2:
            return None
        payload_part = token_parts[1]
        padding = len(payload_part) % 4
        if padding:
            payload_part += '=' * (4 - padding)
        payload = json.loads(base64.urlsafe_b64decode(payload_part))
        return payload.get("sub")
    except:
        return None

def get_user_role_from_token(access_token):
    try:
        token_parts = access_token.split('.')
        if len(token_parts) < 2:
            return None
        payload_part = token_parts[1]
        padding = len(payload_part) % 4
        if padding:
            payload_part += '=' * (4 - padding)
        payload = json.loads(base64.urlsafe_b64decode(payload_part))
        return payload.get("role")
    except:
        return None

def get_user_from_token(user_service, access_token):
    user_id = get_user_id_from_token(access_token)
    if not user_id:
        return None
    try:
        logged_user = user_service.get_user(user_id)
        if logged_user and isinstance(logged_user, dict):
            return logged_user
    except:
        pass
    return None

def get_user_from_email_fallback(user_service, email):
    try:
        user_response = user_service.list_users()
        if isinstance(user_response, list) and len(user_response) > 0:
            return next((u for u in user_response if u.get("email") == email), None)
    except:
        pass
    return None

def handle_login_success(access_token, refresh_token, logged_user):
    set_token(access_token)
    set_refresh_token(refresh_token)
    set_user(logged_user)
    show_success(f"Welcome, {logged_user.get('name', 'User')}!")
    st.rerun()

def handle_login_error(error_msg):
    if "401" in error_msg or "Unauthorized" in error_msg:
        show_error("Invalid credentials")
    else:
        show_error(f"Login error: {error_msg}")

def process_login(auth_service, user_service, login_data):
    response = auth_service.login(login_data["email"], login_data["password"])
    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    
    if not access_token or not refresh_token:
        show_error("Invalid server response")
        return
    
    set_token(access_token)
    set_refresh_token(refresh_token)
    
    logged_user = get_user_from_email_fallback(user_service, login_data["email"])
    if logged_user:
        set_user(logged_user)
        show_success(f"Welcome, {logged_user.get('name', 'User')}!")
        st.rerun()
        return
    
    logged_user = get_user_from_token(user_service, access_token)
    if logged_user:
        set_user(logged_user)
        show_success(f"Welcome, {logged_user.get('name', 'User')}!")
        st.rerun()
        return
    
    user_id = get_user_id_from_token(access_token)
    user_role = get_user_role_from_token(access_token)
    if user_id:
        logged_user = {"id": user_id, "email": login_data["email"], "name": "User"}
        if user_role:
            logged_user["role"] = user_role
        set_user(logged_user)
        show_success(f"Welcome!")
        st.rerun()
        return
    
    show_error("Unable to load user data")

def handle_user_registration(auth_service, user_data):
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

def handle_user_update(user_service, selected_user, edit_data, table_action_key):
    try:
        updated_user = user_service.update_user(selected_user["id"], edit_data)
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

def handle_user_deletion(user_service, selected_user, table_action_key, delete_modal_state_key):
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

def render_delete_user_modal(selected_user, table_action_key, delete_modal_state_key, user_service):
    @st.dialog("Delete User Confirmation")
    def delete_confirmation_dialog():
        st.markdown(f"### ⚠️ Delete User: {selected_user.get('name')}")
        st.warning(f"Are you sure you want to delete user **{selected_user.get('name')}** ({selected_user.get('email')})?\n\nThis action **cannot be undone**.")
        
        col_confirm, col_cancel = st.columns(2)
        
        with col_confirm:
            if st.button("Confirm Deletion", type="primary", use_container_width=True):
                handle_user_deletion(user_service, selected_user, table_action_key, delete_modal_state_key)
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                if table_action_key in st.session_state:
                    del st.session_state[table_action_key]
                if delete_modal_state_key in st.session_state:
                    del st.session_state[delete_modal_state_key]
                st.rerun()
    
    delete_confirmation_dialog()

def render_login_section(auth_service, user_service):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        login_data = render_login_form()
        if login_data:
            try:
                process_login(auth_service, user_service, login_data)
            except Exception as e:
                handle_login_error(str(e))
    
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

def render_user_list_section(user_service, can_edit_users, can_delete_users):
    if st.session_state.get("users_cache_cleared"):
        del st.session_state.users_cache_cleared
        import time
        time.sleep(0.1)
    
    users = user_service.list_users()
    
    if not users:
        st.info("No users found")
        return
    
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
    if not table_action:
        return
    
    selected_user = table_action["item"]
    
    if table_action["action"] == "edit" and can_edit_users:
        st.markdown("---")
        edit_data = render_user_form(editing_user=selected_user)
        if edit_data:
            handle_user_update(user_service, selected_user, edit_data, table_action_key)
    
    elif table_action["action"] == "delete" and can_delete_users:
        delete_modal_state_key = f"delete_modal_open_{selected_user['id']}"
        st.session_state[delete_modal_state_key] = True
        render_delete_user_modal(selected_user, table_action_key, delete_modal_state_key, user_service)
        if delete_modal_state_key not in st.session_state:
            st.rerun()

def render_user_management_section(auth_service, user_service, can_manage_users, can_register_users, can_edit_users, can_delete_users):
    tabs = st.tabs(["Login", "Manage Users"])
    
    with tabs[0]:
        st.markdown("### Change User")
        st.info("You are already authenticated. Logout to sign in with another account.")
    
    with tabs[1]:
        if not can_manage_users:
            st.warning("You do not have permission to manage users. Only Administrators and Managers can access this functionality.")
            return
        
        col_create, col_list = st.columns([1, 2])
        
        with col_create:
            if can_register_users:
                st.markdown("#### Register User")
                with st.container():
                    user_data = render_user_form()
                if user_data:
                    handle_user_registration(auth_service, user_data)
            else:
                st.info("Only Administrators and Managers can register users.")
        
        with col_list:
            st.markdown("#### User List")
            try:
                render_user_list_section(user_service, can_edit_users, can_delete_users)
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

if token and user and not is_authenticated():
    set_user(user)
    set_token(token)

if not is_authenticated():
    render_login_section(auth_service, user_service)
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
    render_user_management_section(auth_service, user_service, can_manage_users, can_register_users, can_edit_users, can_delete_users)
