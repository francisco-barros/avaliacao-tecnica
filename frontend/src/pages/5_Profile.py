import streamlit as st
import sys
import os

src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services import UserService
from state.auth_state import (
    is_authenticated,
    get_user,
    get_user_role,
    logout,
    set_user,
    get_token
)
from utils.helpers import show_error, show_success, show_info
from utils.formatters import format_role
from components.forms.profile_form import render_profile_form

st.set_page_config(
    page_title="Profile / Settings",
    page_icon="👤",
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

def handle_profile_update(user_service, user_id, profile_data):
    try:
        response = user_service.update_user(user_id, profile_data)
        
        current_user = get_user()
        updated_user = {}
        
        if isinstance(response, dict):
            if "data" in response and isinstance(response["data"], dict):
                updated_user = response["data"].copy()
            elif isinstance(response, dict) and ("id" in response or "name" in response or "email" in response):
                updated_user = response.copy()
        
        updated_user["id"] = user_id
        
        updated_user["email"] = profile_data.get("email", "")
        if not updated_user.get("email") and current_user:
            updated_user["email"] = current_user.get("email", "")
        
        updated_user["name"] = profile_data.get("name", "")
        if not updated_user.get("name") and current_user:
            updated_user["name"] = current_user.get("name", "")
        
        if current_user and current_user.get("role"):
            updated_user["role"] = current_user.get("role")
        elif updated_user.get("role"):
            pass
        else:
            updated_user["role"] = "member"
        
        set_user(updated_user)
        show_success("Profile updated successfully!")
        st.rerun()
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            if "only update your own profile" in error_msg.lower():
                show_error("You can only update your own profile")
            elif "only administrators can change" in error_msg.lower() or "role" in error_msg.lower():
                show_error("Only administrators can change user roles")
            else:
                show_error("You do not have permission to perform this action")
        elif "404" in error_msg:
            show_error("User not found")
        elif "409" in error_msg or "Conflict" in error_msg or "already in use" in error_msg.lower():
            show_error("Email already in use")
        else:
            show_error(f"Error updating profile: {error_msg}")

def render_profile_info_section(current_user, user_role):
    st.markdown("### Profile Information")
    
    user_id = current_user.get("id", "") if current_user else ""
    
    email_value = current_user.get("email") if current_user else None
    if not email_value:
        email_value = "N/A"
    
    name_value = current_user.get("name") if current_user else None
    if not name_value:
        name_value = "N/A"
    
    st.text_input(
        "Email",
        value=email_value,
        disabled=True,
        key=f"profile_info_email_{user_id}"
    )
    
    st.text_input(
        "Name",
        value=name_value,
        disabled=True,
        key=f"profile_info_name_{user_id}"
    )
    
    role_value = "N/A"
    if user_role:
        role_str = str(user_role).lower()
        role_value = format_role(role_str)
    
    st.text_input(
        "Role",
        value=role_value,
        disabled=True,
        key=f"profile_info_role_{user_id}"
    )

def render_profile_edit_section(user_service, user_id):
    st.markdown("---")
    
    current_user = get_user()
    if not current_user:
        st.error("Unable to load user information")
        return
    
    profile_data = render_profile_form(current_user)
    if profile_data:
        handle_profile_update(user_service, user_id, profile_data)

def render_profile_content(user_service):
    current_user = get_user()
    user_role = current_user.get("role") if current_user else None
    user_id = current_user.get("id") if current_user else None
    
    if not user_role and current_user:
        access_token = get_token()
        if access_token:
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
                    token_role = payload.get("role")
                    if token_role:
                        user_role = token_role
                        current_user["role"] = token_role
                        set_user(current_user)
            except:
                pass
    
    if not user_id:
        st.error("Unable to load user information")
        return
    
    tabs = st.tabs(["Profile Info", "Edit Profile"])
    
    with tabs[0]:
        render_profile_info_section(current_user, user_role)
    
    with tabs[1]:
        try:
            render_profile_edit_section(user_service, user_id)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                show_error("Session expired. Please login again.")
                logout()
                st.rerun()
            else:
                show_error(f"Error loading profile: {error_msg}")

load_css()

if "user_service" not in st.session_state:
    st.session_state.user_service = UserService()

user_service = st.session_state.user_service

st.title("👤 Profile / Settings")

if not is_authenticated():
    st.warning("Please login to access your profile")
    st.stop()

current_user = get_user()
if not current_user:
    st.error("Unable to load user information")
    st.stop()

user_role = current_user.get("role")
if not user_role:
    access_token = get_token()
    if access_token:
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
                token_role = payload.get("role")
                if token_role:
                    user_role = token_role
                    current_user["role"] = token_role
                    set_user(current_user)
        except:
            pass

col_header, col_logout = st.columns([5, 1])
with col_header:
    current_user_for_header = get_user()
    user_name = current_user_for_header.get("name", "User") if current_user_for_header else "User"
    st.markdown(f"### Welcome, {user_name}")
with col_logout:
    if st.button("Logout", use_container_width=True):
        logout()
        show_info("Logout successful")
        st.rerun()

st.markdown("---")

render_profile_content(user_service)

