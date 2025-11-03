import streamlit as st
import sys
import os
from typing import Optional, Dict, Callable

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.validators import validate_email, validate_password, validate_required
from utils.helpers import show_error
from utils.constants import UserRole

def render_user_form(editing_user: Optional[Dict] = None, on_submit: Optional[Callable] = None) -> Optional[Dict]:
    is_edit = editing_user is not None
    
    if is_edit:
        st.markdown("### Edit User")
        form_key = f"user_form_edit_{editing_user.get('id', '')}"
    else:
        st.markdown("### Register New User")
        form_key = "user_form_register"
    
    with st.form(form_key, clear_on_submit=not is_edit):
        name_key = f"{form_key}_name"
        email_key = f"{form_key}_email"
        password_key = f"{form_key}_password"
        role_key = f"{form_key}_role"
        
        name = st.text_input(
            "Name",
            value=editing_user.get("name", "") if is_edit else "",
            key=name_key
        )
        
        email = st.text_input(
            "Email",
            value=editing_user.get("email", "") if is_edit else "",
            key=email_key,
            disabled=is_edit
        )
        
        if not is_edit:
            password = st.text_input("Password", type="password", key=password_key)
        else:
            password = None
        
        role_options = [UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER]
        
        if is_edit:
            user_role = editing_user.get("role", UserRole.MEMBER)
            if isinstance(user_role, str):
                user_role = user_role.lower()
            try:
                role_index = role_options.index(user_role)
            except ValueError:
                role_index = role_options.index(UserRole.MEMBER)
        else:
            role_index = 0
        
        role = st.selectbox(
            "Role",
            role_options,
            index=role_index,
            key=role_key,
            format_func=lambda x: {
                UserRole.ADMIN: "Admin",
                UserRole.MANAGER: "Manager",
                UserRole.MEMBER: "Member"
            }.get(x, x)
        )
        
        submit_label = "Update" if is_edit else "Register"
        submit_button = st.form_submit_button(submit_label, use_container_width=True)
        
        if submit_button:
            if not validate_required(name):
                show_error("Name is required")
                return None
            
            if not validate_email(email):
                show_error("Invalid email")
                return None
            
            if not is_edit and not validate_password(password):
                show_error("Password must be at least 6 characters")
                return None
            
            data = {"name": name, "email": email, "role": role}
            if not is_edit:
                data["password"] = password
            
            return data
    
    return None

