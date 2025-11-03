import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go

src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services import ProjectService, TaskService
from state.auth_state import (
    is_authenticated,
    get_user,
    get_user_role,
    logout
)
from utils.constants import UserRole, ProjectStatus, TaskStatus
from utils.helpers import show_error, show_info

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
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
    
    dashboard_css = """
    <style>
    .metric-card {
        padding: 1.5rem !important;
        border-radius: 12px !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 1rem !important;
        min-height: 120px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    .metric-card-planned {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
    }
    .metric-card-progress {
        background: linear-gradient(135deg, #5a67d8 0%, #434190 100%) !important;
    }
    .metric-card-completed {
        background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%) !important;
    }
    .metric-card-total {
        background: linear-gradient(135deg, #718096 0%, #4a5568 100%) !important;
    }
    .metric-card-pending {
        background: linear-gradient(135deg, #ed8936 0%, #c05621 100%) !important;
    }
    .metric-card-done {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%) !important;
    }
    .metric-card-awaiting {
        background: linear-gradient(135deg, #cbd5e0 0%, #a0aec0 100%) !important;
        color: #2d3748 !important;
    }
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        margin: 0.5rem 0 !important;
    }
    .metric-label {
        font-size: 0.9rem !important;
        opacity: 0.9 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    .project-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    .project-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
    """
    st.markdown(dashboard_css, unsafe_allow_html=True)

def load_projects_and_tasks(project_service, task_service):
    try:
        projects = project_service.list_projects()
        all_tasks = []
        
        for project in projects:
            try:
                project_tasks = task_service.list_tasks(project.get("id"))
                for task in project_tasks:
                    task["project_id"] = project.get("id")
                    task["project_name"] = project.get("name", "Unknown")
                    all_tasks.append(task)
            except:
                pass
        
        return projects, all_tasks
    except Exception as e:
        return [], []

def calculate_project_statistics(projects):
    total = len(projects)
    planned = len([p for p in projects if p.get("status") == ProjectStatus.PLANNED])
    in_progress = len([p for p in projects if p.get("status") == ProjectStatus.IN_PROGRESS])
    completed = len([p for p in projects if p.get("status") == ProjectStatus.COMPLETED])
    
    return {
        "total": total,
        "planned": planned,
        "in_progress": in_progress,
        "completed": completed
    }

def calculate_task_statistics(tasks):
    total = len(tasks)
    pending = len([t for t in tasks if t.get("status") == TaskStatus.PENDING])
    in_progress = len([t for t in tasks if t.get("status") == TaskStatus.IN_PROGRESS])
    done = len([t for t in tasks if t.get("status") == TaskStatus.DONE])
    awaiting = len([t for t in tasks if t.get("status") == TaskStatus.AWAITING_REASSIGNMENT])
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "awaiting": awaiting
    }

def calculate_project_progress(project, all_tasks):
    project_tasks = [t for t in all_tasks if t.get("project_id") == project.get("id")]
    
    if not project_tasks:
        return 0
    
    done_count = len([t for t in project_tasks if t.get("status") == TaskStatus.DONE])
    progress = int((done_count / len(project_tasks)) * 100)
    
    return progress

def render_metric_card_html(label, value, gradient_class):
    return f"""
    <div class="metric-card {gradient_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

def render_project_metrics(project_stats):
    st.markdown("### 📁 Project Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_metric_card_html("Total Projects", project_stats["total"], "metric-card-total"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_metric_card_html("Planned", project_stats["planned"], "metric-card-planned"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card_html("In Progress", project_stats["in_progress"], "metric-card-progress"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_metric_card_html("Completed", project_stats["completed"], "metric-card-completed"), unsafe_allow_html=True)

def render_task_metrics(task_stats):
    st.markdown("### ✅ Task Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(render_metric_card_html("Total Tasks", task_stats["total"], "metric-card-total"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_metric_card_html("Pending", task_stats["pending"], "metric-card-pending"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card_html("In Progress", task_stats["in_progress"], "metric-card-progress"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_metric_card_html("Done", task_stats["done"], "metric-card-done"), unsafe_allow_html=True)
    
    with col5:
        st.markdown(render_metric_card_html("Awaiting Assignee", task_stats["awaiting"], "metric-card-awaiting"), unsafe_allow_html=True)

def get_status_badge_color(status):
    if status == ProjectStatus.COMPLETED:
        return "#4facfe"
    elif status == ProjectStatus.IN_PROGRESS:
        return "#f5576c"
    else:
        return "#667eea"

def render_projects_overview(projects, all_tasks):
    if not projects:
        st.info("No projects available")
        return
    
    st.markdown("### 📊 Projects Overview")
    
    for project in projects:
        progress = calculate_project_progress(project, all_tasks)
        status = project.get("status", ProjectStatus.PLANNED)
        project_tasks = [t for t in all_tasks if t.get("project_id") == project.get("id")]
        total_tasks = len(project_tasks)
        done_tasks = len([t for t in project_tasks if t.get("status") == TaskStatus.DONE])
        
        status_display = status.replace("_", " ").title()
        status_color = get_status_badge_color(status)
        
        project_card = f"""
        <div class="project-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #333;">{project.get('name', 'Unnamed Project')}</h3>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">{project.get("description", "No description")}</p>
                </div>
                <div style="text-align: right;">
                    <span style="background: {status_color}; color: white; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                        {status_display}
                    </span>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.9rem; color: #666;">Progress</span>
                    <span style="font-weight: bold; color: #333;">{progress}%</span>
                </div>
                <div style="background: #e0e0e0; border-radius: 10px; height: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {progress}%; transition: width 0.3s;"></div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
                    {done_tasks} of {total_tasks} tasks completed
                </div>
            </div>
        </div>
        """
        st.markdown(project_card, unsafe_allow_html=True)

def render_project_status_chart(project_stats):
    labels = ["Planned", "In Progress", "Completed"]
    values = [
        project_stats["planned"],
        project_stats["in_progress"],
        project_stats["completed"]
    ]
    
    colors = ["#0066FF", "#FF6600", "#00CC66"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo="label+percent",
        textposition="outside"
    )])
    
    fig.update_layout(
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
        height=400
    )
    
    st.markdown("#### Project Status Distribution")
    st.plotly_chart(fig, use_container_width=True)

def render_task_status_chart(task_stats):
    labels = ["Pending", "In Progress", "Done", "Awaiting Assignee"]
    values = [
        task_stats["pending"],
        task_stats["in_progress"],
        task_stats["done"],
        task_stats["awaiting"]
    ]
    
    colors = ["#FFCC00", "#0066FF", "#00CC66", "#FF6600"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo="label+percent",
        textposition="outside"
    )])
    
    fig.update_layout(
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
        height=400
    )
    
    st.markdown("#### Task Status Distribution")
    st.plotly_chart(fig, use_container_width=True)

def render_dashboard_content(project_service, task_service):
    if st.session_state.get("projects_cache_cleared"):
        del st.session_state.projects_cache_cleared
    if st.session_state.get("tasks_cache_cleared"):
        del st.session_state.tasks_cache_cleared
    
    projects, all_tasks = load_projects_and_tasks(project_service, task_service)
    
    if not projects:
        st.info("No projects found. Create a project to see statistics.")
        return
    
    project_stats = calculate_project_statistics(projects)
    task_stats = calculate_task_statistics(all_tasks)
    
    st.markdown("#### Key Metrics")
    render_project_metrics(project_stats)
    render_task_metrics(task_stats)
    
    st.markdown("---")
    
    has_project_data = project_stats["total"] > 0
    has_task_data = task_stats["total"] > 0
    
    if has_project_data or has_task_data:
        if has_project_data and has_task_data:
            col1, spacer, col2 = st.columns([1, 0.1, 1])
            
            with col1:
                render_project_status_chart(project_stats)
            
            with spacer:
                st.empty()
            
            with col2:
                render_task_status_chart(task_stats)
        elif has_project_data:
            render_project_status_chart(project_stats)
        elif has_task_data:
            render_task_status_chart(task_stats)
    
    st.markdown("---")
    
    render_projects_overview(projects, all_tasks)


load_css()

if "project_service" not in st.session_state:
    st.session_state.project_service = ProjectService()

if "task_service" not in st.session_state:
    st.session_state.task_service = TaskService()

project_service = st.session_state.project_service
task_service = st.session_state.task_service

st.title("📊 Dashboard — Overview of Projects and Progress")

if not is_authenticated():
    st.warning("Please login to access the dashboard")
    st.stop()

user = get_user()
user_role = get_user_role()

col_header, col_logout = st.columns([5, 1])
with col_header:
    st.markdown(f"### Welcome, {user.get('name', 'User')}")
with col_logout:
    if st.button("Logout", use_container_width=True):
        logout()
        show_info("Logout successful")
        st.rerun()

st.markdown("---")

try:
    render_dashboard_content(project_service, task_service)
except Exception as e:
    error_msg = str(e)
    if "401" in error_msg or "Unauthorized" in error_msg:
        show_error("Session expired. Please login again.")
        logout()
        st.rerun()
    elif "403" in error_msg or "Forbidden" in error_msg:
        show_error("You do not have permission to view dashboard data")
    else:
        show_error(f"Error loading dashboard: {error_msg}")

