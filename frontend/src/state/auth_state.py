import streamlit as st

TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"
USER_KEY = "user"

def get_token():
    if TOKEN_KEY not in st.session_state:
        return None
    return st.session_state[TOKEN_KEY]

def set_token(token):
    if token:
        st.session_state[TOKEN_KEY] = token

def get_refresh_token():
    if REFRESH_TOKEN_KEY not in st.session_state:
        return None
    return st.session_state[REFRESH_TOKEN_KEY]

def set_refresh_token(token):
    if token:
        st.session_state[REFRESH_TOKEN_KEY] = token

def get_user():
    if USER_KEY not in st.session_state:
        return None
    return st.session_state[USER_KEY]

def set_user(user):
    if user:
        st.session_state[USER_KEY] = user

def is_authenticated():
    token = get_token()
    user = get_user()
    return token is not None and token != "" and user is not None

def logout():
    if TOKEN_KEY in st.session_state:
        del st.session_state[TOKEN_KEY]
    if REFRESH_TOKEN_KEY in st.session_state:
        del st.session_state[REFRESH_TOKEN_KEY]
    if USER_KEY in st.session_state:
        del st.session_state[USER_KEY]

def get_user_role():
    user = get_user()
    if user and isinstance(user, dict):
        return user.get("role")
    return None

