# Project Management System

Complete project management system with Flask REST API backend and Streamlit frontend.

## Features

- JWT authentication with role-based access control
- Project and task management
- User profile management (self-service profile updates)
- Real-time updates via WebSockets
- Redis caching (1 minute TTL for all queries)
- Swagger/OpenAPI documentation

## Installation

### With Docker (Recommended)

Builds and runs both backend and frontend services together:

```bash
git clone <repository-url>
cd avaliacao-tecnica
docker compose up --build
```

This command will:
- Build and start the backend API (Flask)
- Build and start the frontend application (Streamlit)
- Start PostgreSQL and Redis services
- Load seed data automatically on first startup

**Services:**
- Frontend (Streamlit): http://localhost:8501
- Backend API: http://localhost:5000
- Swagger UI: http://localhost:5000/apidocs
- PostgreSQL: localhost:5433
- Redis: localhost:6379

**Seed Data:**
Automatically loaded on first startup:
- 8 users (admin, managers, members)
- 6 projects
- 12 tasks

**Test Credentials:**
- Admin: `admin@example.com` / `admin123`
- Manager: `manager1@example.com` / `manager123`
- Member: `member1@example.com` / `member123`

### Running Frontend Separately (Development)

To run the frontend locally for development:

```bash
cd frontend
pip install -r requirements.txt
streamlit run "src/🔐_Login___User_Management.py"
```

The frontend will be available at http://localhost:8501

**Note:** Make sure the backend API is running (http://localhost:5000) and accessible from the frontend.

### To Do

- Implement login token persistence when reloading the web page
- Implement real-time dashboard data updates in the frontend
- Improve web page layout and responsiveness
- Handle validations and edge cases in the frontend

## Testing

**IMPORTANT**: Prefer testing with Postman collections (`backend/postman/`) as API documentation may contain unexpected errors.

### Backend Tests
```bash
cd backend
pytest --cov=src
```

Coverage: 89%

### API Testing
Use Postman collection for reliable endpoint testing:
- Import `backend/postman/postman_collection.json`
- Import `backend/postman/postman_environment.json`
- See `backend/postman/README.md` for details

## Documentation

- Swagger UI: http://localhost:5000/apidocs
- OpenAPI Spec: http://localhost:5000/apispec.json

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/register` - Register new user (Admin/Manager only)

### Users
- `GET /api/users` - List all users (Admin/Manager only)
- `GET /api/users/<user_id>` - Get user by ID (Admin/Manager only)
- `PATCH /api/users/<user_id>` - Update user (Users can update their own profile, Admin can update any user. Only Admin can change roles)
- `DELETE /api/users/<user_id>` - Delete user (Admin only)

### Projects
- `POST /api/projects` - Create new project (Manager/Admin only)
- `GET /api/projects` - List user projects
- `GET /api/projects/<project_id>` - Get project by ID
- `PATCH /api/projects/<project_id>` - Update project (Manager/Admin only)
- `DELETE /api/projects/<project_id>` - Delete project (Manager/Admin only)
- `POST /api/projects/<project_id>/members` - Add member to project (Manager/Admin only)
- `DELETE /api/projects/<project_id>/members/<user_id>` - Remove member from project (Manager/Admin only)

### Tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/project/<project_id>` - List project tasks
- `PATCH /api/tasks/<task_id>/status` - Update task status (only assignee can update)
- `PATCH /api/tasks/<task_id>/assignee` - Reassign task to a new assignee (Admin, Manager or Project Owner only)

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Docker Compose                      │
├─────────────────┬───────────────────────────────────────┤
│   Backend API   │         Frontend (Streamlit)          │
│   Flask:5000    │            Streamlit:8501             │
└─────┬───────────┴───────────────────────────────────────┘
      │
      ├──────────────┬──────────────────┐
      │              │                  │
   PostgreSQL      Redis           SocketIO
   Port:5433     Port:6379      (WebSockets)
```

### Backend Structure

```
backend/
├── src/                          # Source code
│   ├── auth/                     # Authentication module
│   │   └── routes.py            # Login, register, refresh
│   ├── user/                     # User management
│   │   ├── models.py            # User model with soft delete
│   │   ├── repository.py        # User database operations
│   │   ├── routes.py            # User endpoints
│   │   └── service.py           # User business logic
│   ├── project/                  # Project management
│   │   ├── models.py            # Project model with soft delete
│   │   ├── repository.py        # Project database operations
│   │   ├── routes.py            # Project endpoints
│   │   └── service.py           # Project business logic
│   ├── task/                     # Task management
│   │   ├── models.py            # Task model with soft delete
│   │   ├── repository.py        # Task database operations
│   │   ├── routes.py            # Task endpoints
│   │   └── service.py           # Task business logic
│   ├── access_control/           # Authorization decorators
│   │   └── decorators.py        # Role-based access control
│   ├── cache/                    # Redis caching
│   │   ├── __init__.py
│   │   └── client.py            # Cache client
│   ├── log/                      # Logging system
│   │   ├── __init__.py
│   │   ├── models.py            # Log model
│   │   ├── repository.py        # Log database operations
│   │   ├── service.py           # Log service + app logging
│   │   └── decorator.py         # Log decorator
│   ├── http_responses/           # Standardized HTTP responses
│   │   ├── __init__.py
│   │   └── responses.py         # Response helpers
│   ├── extensions.py             # Flask extensions (DB, JWT, etc.)
│   ├── factory.py                # Application factory
│   ├── settings.py               # Configuration
│   ├── register_blueprints.py   # Route registration
│   ├── soft_delete.py            # Soft delete mixin
│   └── main.py                   # Application entry point
├── tests/                        # Test suite
│   ├── conftest.py              # Shared fixtures
│   ├── test_auth.py             # Auth tests
│   ├── test_users.py            # User tests
│   ├── test_projects.py         # Project tests
│   ├── test_projects_tasks.py   # Projects and tasks integration tests
│   ├── test_tasks.py            # Task tests
│   └── test_services.py         # Service tests
├── postman/                      # API testing
│   ├── postman_collection.json  # All endpoints
│   ├── postman_environment.json # Environment vars
│   └── README.md                # Postman collection documentation
├── seed/                         # Seed data
│   ├── users.json               # Test users
│   ├── projects.json            # Test projects
│   └── tasks.json               # Test tasks
├── scripts/                      # Utility scripts
│   └── load_seed_data.py        # Seed loader
├── docs/                         # Documentation
│   └── Avaliacao_Tecnica_Python.pdf  # Technical assessment document
├── Dockerfile                    # Backend container
├── requirements.txt              # Python dependencies
└── pytest.ini                    # Test configuration
```

### Frontend Structure

```
frontend/
├── src/                         # Source code
│   ├── 🔐_Login___User_Management.py  # Main entry point (Login/User Management page)
│   ├── pages/                   # Streamlit pages
│   │   ├── 2_Projects.py        # Projects management page
│   │   ├── 3_Tasks.py           # Tasks management page
│   │   ├── 4_Dashboard.py       # Dashboard with project and task overview
│   │   └── 5_Profile.py         # Profile/Settings page
│   ├── components/              # Reusable components
│   │   ├── forms/               # Form components
│   │   │   ├── login_form.py    # Login form
│   │   │   ├── user_form.py     # User creation/editing form
│   │   │   ├── project_form.py  # Project creation/editing form
│   │   │   ├── task_form.py     # Task creation/editing form
│   │   │   └── profile_form.py  # Profile editing form
│   │   ├── tables/              # Table components
│   │   │   ├── base_grid_table.py  # Base grid table component
│   │   │   ├── users_table.py   # Users table
│   │   │   ├── projects_table.py  # Projects table
│   │   │   └── tasks_table.py   # Tasks table
│   │   ├── managers/            # Management components
│   │   │   └── member_manager.py  # Project member management
│   │   └── widgets/             # Widget components
│   ├── services/                # API services
│   │   ├── api/                 # Service classes
│   │   │   ├── auth_service.py  # Authentication service
│   │   │   ├── user_service.py  # User service
│   │   │   ├── project_service.py  # Project service
│   │   │   └── task_service.py  # Task service
│   │   └── base/                # Base API client
│   │       └── api_client.py    # Base API client with authentication
│   ├── state/                   # State management
│   │   └── auth_state.py        # Authentication state and token management
│   ├── utils/                   # Utilities
│   │   ├── constants.py         # Constants (UserRole, etc.)
│   │   ├── formatters.py        # Data formatters
│   │   ├── helpers.py           # Helper functions
│   │   └── validators.py       # Validation functions
│   ├── config/                  # Configuration
│   │   ├── api_config.py        # API endpoints configuration
│   │   └── settings.py          # Application settings
│   └── styles/                  # CSS styles
│       ├── main.css             # Main styles
│       ├── components.css       # Component styles
│       └── users_table.css      # Users table specific styles
├── Dockerfile                   # Frontend container
├── requirements.txt             # Python dependencies
└── README.md                    # Frontend documentation
```

### Architecture Patterns

- **Layered Architecture**: Routes → Service → Repository → Models
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **Factory Pattern**: Application initialization
- **Decorator Pattern**: Cross-cutting concerns (auth, logging)

## Cache Strategy

Redis cache (1 minute TTL) is enabled for the following operations:
- `GET /api/users` - List all users
- `GET /api/users/<id>` - Get user by ID
- `GET /api/projects` - List user projects
- `GET /api/projects/<id>` - Get project by ID
- `GET /api/tasks/project/<project_id>` - List project tasks

Cache is automatically invalidated on any create/update/delete operations.

## License

Technical assessment project.