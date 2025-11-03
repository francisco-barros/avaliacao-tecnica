# Postman Collection

Complete collection to test all API endpoints.

## Import

1. Open Postman
2. Click **Import**
3. Import:
   - `postman_collection.json`
   - `postman_environment.json`

## Configure

Select environment **"Project Management API - Local"** in Postman.

## Testing Recommendation

**PREFERRED METHOD**: Use this Postman collection for API testing instead of Swagger documentation, as it provides more reliable and accurate endpoint testing.

## Quick Start

1. Login (`Auth > Login`)
2. List Users (`Users > List Users`)
3. Create Project (`Projects > Create Project`)
4. Create Task (`Tasks > Create Task`)

## Credentials

- Admin: `admin@example.com` / `admin123`
- Manager: `manager1@example.com` / `manager123`
- Member: `member1@example.com` / `member123`

## Endpoints

**Auth**: Login, Refresh, Register

**Users**: List, Get, Update (Users can update own profile, Admin can update any user), Delete

**Projects**: Create, List, Get, Update, Delete, Add Member, Remove Member

**Tasks**: Create, List, Update Status, Reassign

## Auto Variables

Collection automatically saves:
- `access_token` and `refresh_token` after login
- `user_id`, `project_id`, `task_id` after creation

## Cache Strategy

**Note**: Redis cache (1 minute TTL) is enabled for all query operations:
- `GET /api/users` (list and get by ID)
- `GET /api/projects` (list and get by ID)
- `GET /api/tasks/project/<project_id>` (list tasks)

Cache is automatically invalidated on any create/update/delete operations.

## Docker

```bash
docker compose up -d
```

Then use `http://localhost:5000` as base_url.