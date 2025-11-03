# Frontend - Project Management System

Streamlit frontend for the Project Management System.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
streamlit run "src/🔐_Login___User_Management.py"
```

Access the application at: http://localhost:8501

### To Do

- Implement login token persistence when reloading the web page
- Implement real-time dashboard data updates in the frontend
- Improve web page layout and responsiveness
- Handle validations and edge cases in the frontend

## Docker

```bash
docker build -t frontend .
docker run -p 8501:8501 frontend
```

## Pages

### Login / User Management
- User authentication (login/logout)
- User management for administrators (create, update, delete users)
- Role-based access control

### Dashboard
- Overview of projects and tasks
- Key metrics (project and task statistics)
- Project status distribution (donut chart)
- Task status distribution (donut chart)
- Project cards with progress visualization

### Projects
- Create and manage projects
- Add/remove members from projects
- View project tasks
- Project owner and manager permissions

### Tasks
- Create and assign tasks to users
- Update task status (assignee only)
- Reassign tasks (admin, manager, or project owner)
- Filter tasks by project and status

### Profile / Settings
- View profile information (name, email, role)
- Edit own profile (name and email)
- Logout functionality
- Real-time data synchronization after updates

## Structure

- `src/🔐_Login___User_Management.py` - Main entry point (Login/User Management page)
- `src/pages/` - Streamlit pages
  - `2_Projects.py` - Project management
  - `3_Tasks.py` - Task management
  - `4_Dashboard.py` - Dashboard with project and task overview
  - `5_Profile.py` - User profile and settings
- `src/components/` - Reusable components
  - `forms/` - Form components
    - `login_form.py` - Login form
    - `user_form.py` - User creation/editing form
    - `project_form.py` - Project creation/editing form
    - `task_form.py` - Task creation/editing form
    - `profile_form.py` - Profile editing form
  - `tables/` - Table components
    - `base_grid_table.py` - Base grid table component
    - `users_table.py` - Users table
    - `projects_table.py` - Projects table
    - `tasks_table.py` - Tasks table
  - `managers/` - Management components
    - `member_manager.py` - Project member management
  - `widgets/` - Widget components
- `src/services/` - API services
  - `api/` - Service classes for API communication
    - `auth_service.py` - Authentication service
    - `user_service.py` - User service
    - `project_service.py` - Project service
    - `task_service.py` - Task service
  - `base/` - Base API client
    - `api_client.py` - Base API client with authentication and error handling
- `src/state/` - State management
  - `auth_state.py` - Authentication state and token management
- `src/utils/` - Utilities
  - `constants.py` - Constants (UserRole, etc.)
  - `formatters.py` - Data formatters
  - `helpers.py` - Helper functions
  - `validators.py` - Validation functions
- `src/config/` - Configuration
  - `api_config.py` - API endpoints configuration
  - `settings.py` - Application settings
- `src/styles/` - CSS styles
  - `main.css` - Main styles
  - `components.css` - Component styles
  - `users_table.css` - Users table specific styles

