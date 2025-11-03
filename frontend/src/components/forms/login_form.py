import streamlit as st
import sys
import os
from typing import Optional, Dict, Callable

src_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.validators import validate_email, validate_password
from utils.helpers import show_error, show_success

def render_login_form(on_success: Optional[Callable] = None) -> Optional[Dict]:
    st.markdown("### Login")
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not validate_email(email):
                show_error("Invalid email")
                return None
            
            if not validate_password(password):
                show_error("Password must be at least 6 characters")
                return None
            
            return {"email": email, "password": password}
    
    return None

