# Synapze Task Management Backend

FastAPI backend for a multi-role internal task management system.

## Features

- JWT authentication
- Role-based access control for `admin`, `manager`, and `employee`
- User management API
- Task CRUD API
- Assigned-employee task visibility
- Task comments
- Task status audit history
- Background notification hooks for task assignment and status updates
- SQLAlchemy ORM models and Alembic migrations
- Pytest API coverage

## Setup

```bash
python3 -m pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/synapze
SECRET_KEY=change-this-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=
MAIL_FROM=no-reply@synapze.local
```

Run migrations:

```bash
python3 -m alembic upgrade head
```

Seed the default admin:

```bash
python3 -m app.scripts.seed_admin
```

Default seeded credentials:

```text
email: admin@test.com
password: admin123
```

Run the API:

```bash
python3 -m uvicorn app.main:app --reload
```

## Main Endpoints

- `POST /api/v1/login`
- `GET /api/v1/users`
- `POST /api/v1/users`
- `PATCH /api/v1/users/{user_id}`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `DELETE /api/v1/tasks/{task_id}`
- `GET /api/v1/tasks/{task_id}/history`
- `POST /api/v1/tasks/{task_id}/comments`
- `GET /api/v1/tasks/{task_id}/comments`

## Tests

```bash
python3 -m pytest -q
```
