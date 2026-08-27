# TaskFlow API

TaskFlow is a FastAPI backend for project-owned task management. It includes JWT authentication, project and task CRUD, cached task filtering, background notification creation, health/metrics endpoints, Docker Compose, and CI.

## Run From A Clean Clone

```bash
docker compose up --build
```

The API starts at `http://localhost:8000`.

Useful endpoints:

- `POST /api/v1/signup` creates a user.
- `POST /api/v1/login` returns a bearer token. Send form fields `username` and `password`.
- `POST /api/v1/projects` creates a project for the authenticated user.
- `GET /api/v1/projects` lists only the authenticated user's projects.
- `GET /api/v1/projects/{project_id}`, `PATCH /api/v1/projects/{project_id}`, `PUT /api/v1/projects/{project_id}`, and `DELETE /api/v1/projects/{project_id}` manage a single owned project.
- `POST /api/v1/tasks` creates a task inside one of the authenticated user's projects.
- `GET /api/v1/tasks?status=todo&assignee_id=1&due_from=2026-08-01T00:00:00&due_to=2026-09-01T00:00:00&limit=20&offset=0` filters tasks with pagination.
- `GET /api/v1/tasks/{task_id}`, `PATCH /api/v1/tasks/{task_id}`, `PUT /api/v1/tasks/{task_id}`, and `DELETE /api/v1/tasks/{task_id}` manage a single owned task.
- `GET /api/v1/notifications` lists notification records for tasks in the authenticated user's projects.
- `POST /api/v1/contacts` accepts contact messages; `GET /api/v1/contacts` is admin-only and supports `name` and `email` query filters.
- `GET /health` and `GET /metrics` expose basic operational status.

For local development without Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY=local-dev-secret
alembic upgrade head
uvicorn app.main:app --reload
```

## Architecture

FastAPI handles the HTTP API, SQLAlchemy owns persistence, PostgreSQL is the production database, Redis backs task-list caching, and Celery handles notification work outside the request path. In tests and simple local runs, `BACKGROUND_JOBS=local` uses FastAPI background tasks and the cache falls back to an in-process store when `REDIS_URL` is empty.

Project ownership is the authorization boundary. Task reads and writes join through projects, so users receive `404` for projects or tasks they do not own instead of being able to infer another user's records. Task-list cache keys are scoped by owner and filter parameters, and task/project writes invalidate that owner's cached task lists.

Notifications are recorded in the `notifications` table. Reassignment and status-change notifications are enqueued from task writes. Overdue task notifications are created by the Celery beat schedule, which scans every minute for incomplete tasks whose due dates have passed and have not already been notified.

## Deployment Path

I chose a documented deployment path rather than a live hosted URL. A typical Render/Railway/Fly deployment uses:

1. Provision PostgreSQL and Redis.
2. Deploy the API container with `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`, `BACKGROUND_JOBS=celery`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND`.
3. Run `alembic upgrade head` during release.
4. Run a separate worker process with `celery -A app.worker:celery_app worker -B --loglevel=info`.
5. Route health checks to `/health`.

## Tests And CI

Run locally with:

```bash
ruff check app tests
pytest
```

The GitHub Actions workflow in `.github/workflows/ci.yml` runs lint and tests on push and pull request.


