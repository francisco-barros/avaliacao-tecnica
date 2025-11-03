import streamlit as st
import sys
import os
from typing import Optional, Dict

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.validators import validate_email, validate_required
from utils.helpers import show_error

def render_profile_form(current_user: Dict) -> Optional[Dict]:
    st.markdown("### Edit Profile")
    user_id = current_user.get("id", "")
    form_key = f"profile_form_edit_{user_id}"
    
    with st.form(form_key, clear_on_submit=False):
        name_key = f"{form_key}_name"
        email_key = f"{form_key}_email"
        
        name = st.text_input(
            "Name",
            value=current_user.get("name", ""),
            key=name_key
        )
        
        email = st.text_input(
            "Email",
            value=current_user.get("email", ""),
            key=email_key
        )
        
        submit_button = st.form_submit_button("Update Profile", use_container_width=True)
        
        if submit_button:
            if not validate_required(name):
                show_error("Name is required")
                return None
            
            if not validate_email(email):
                show_error("Invalid email")
                return None
            
            data = {"name": name, "email": email}
            return data
    
    return None

