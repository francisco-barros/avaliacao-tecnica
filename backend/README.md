# Project Management API

Flask REST API for project and task management with JWT authentication.

## Quick Start

```bash
docker compose up --build
```

API available at: http://localhost:5000

## Testing

**IMPORTANT**: Always test with Postman collections (`postman/`) as API documentation may contain unexpected errors.

```bash
pytest --cov=src
```

Coverage: 89%

### Postman
- Import `postman/postman_collection.json`
- Import `postman/postman_environment.json`
- Run collection for reliable API testing

## API Endpoints

**Auth** (`/api/auth`)
- `POST /login` - Login
- `POST /refresh` - Refresh token
- `POST /register` - Register user

**Users** (`/api/users`)
- `GET /` - List users
- `GET /<id>` - Get user
- `PATCH /<id>` - Update user (Users can update their own profile - name and email. Admin can update any user and change roles)
- `DELETE /<id>` - Delete user (soft delete). Cascades: removes user from owned projects and reassigns tasks to AWAITING_REASSIGNMENT status

**Projects** (`/api/projects`)
- `POST /` - Create project
- `GET /` - List projects
- `GET /<id>` - Get project
- `PATCH /<id>` - Update project
- `DELETE /<id>` - Delete project
- `POST /<id>/members` - Add member
- `DELETE /<id>/members/<user_id>` - Remove member

**Tasks** (`/api/tasks`)
- `POST /` - Create task
- `GET /project/<project_id>` - List tasks
- `PATCH /<task_id>/status` - Update status (only assignee can update)
- `PATCH /<task_id>/assignee` - Reassign task to a new assignee (admin, manager or project owner only)

## Roles

- **ADMIN**: Full access
- **MANAGER**: Create projects/tasks
- **MEMBER**: View projects, update tasks

## Configuration

Environment variables in `docker-compose.yml`:
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `JWT_SECRET_KEY`: JWT secret

## Documentation

- Swagger: http://localhost:5000/apidocs

## Cache Strategy

Redis cache (1 minute TTL) is enabled for the following operations:
- `GET /api/users` - List all users
- `GET /api/users/<id>` - Get user by ID
- `GET /api/projects` - List user projects
- `GET /api/projects/<id>` - Get project by ID
- `GET /api/tasks/project/<project_id>` - List project tasks

Cache is automatically invalidated on any create/update/delete operations.

## Architecture

Layered architecture with Repository and Service patterns.