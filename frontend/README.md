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

- `src/pages/` - Streamlit pages
  - `🔐_Login___User_Management.py` - Login and user management
  - `2_Projects.py` - Project management
  - `3_Tasks.py` - Task management
  - `4_Profile.py` - User profile and settings
- `src/components/` - Reusable components
  - `forms/` - Form components (profile_form, user_form, project_form, task_form)
  - `tables/` - Table components (users_table, projects_table, tasks_table)
  - `managers/` - Management components (member_manager)
- `src/services/` - API services
  - `api/` - Service classes for API communication (AuthService, UserService, ProjectService, TaskService)
  - `base/` - Base API client with authentication and error handling
- `src/state/` - State management
  - `auth_state.py` - Authentication state and token management
- `src/utils/` - Utilities
  - Validators, formatters, helpers
- `src/config/` - Configuration
  - API endpoints and configuration
- `src/styles/` - CSS styles
  - Component and layout styles

