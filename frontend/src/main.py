import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Project Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

