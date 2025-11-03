# Project Management System

Complete project management system with Flask REST API backend and Streamlit frontend.

## Features

- JWT authentication with role-based access control
- Project and task management
- Real-time updates via WebSockets
- Redis caching (1 minute TTL for all queries)
- Swagger/OpenAPI documentation

## Installation

### With Docker (Recommended)

```bash
git clone <repository-url>
cd avaliacao-tecnica
docker compose up --build
```

**Services:**
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
- `PATCH /api/users/<user_id>` - Update user (Admin only)
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
│   │   ├── client.py            # Cache client
│   │   └── __init__.py
│   ├── log/                      # Logging system
│   │   ├── models.py            # Log model
│   │   ├── repository.py        # Log database operations
│   │   ├── service.py           # Log service + app logging
│   │   └── decorator.py         # Log decorator
│   ├── http_responses/           # Standardized HTTP responses
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
│   ├── test_tasks.py            # Task tests
│   └── test_services.py         # Service tests
├── postman/                      # API testing
│   ├── postman_collection.json  # All endpoints
│   └── postman_environment.json # Environment vars
├── seed/                         # Seed data
│   ├── users.json               # Test users
│   ├── projects.json            # Test projects
│   └── tasks.json               # Test tasks
├── scripts/                      # Utility scripts
│   └── load_seed_data.py        # Seed loader
├── Dockerfile                    # Backend container
├── requirements.txt              # Python dependencies
└── pytest.ini                    # Test configuration
```

### Frontend Structure (Coming Soon)

```
frontend/
├── src/                         # Source code
├── Dockerfile                   # Frontend container
├── requirements.txt             # Python dependencies
└── README.md
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