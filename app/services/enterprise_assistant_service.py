from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.enterprise_assistant import AssistantAction, AskResponse
from app.schemas.task import TaskCreate
from app.services.task_service import TaskService


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class EnterpriseAssistantService:
    """Small agent-style workflow over the app's real user and task tables."""

    def ask(self, question: str, db: Session) -> AskResponse:
        cleaned_question = " ".join(question.strip().split())
        lowered = cleaned_question.lower()

        if self._is_unsafe_request(lowered):
            return AskResponse(
                question=cleaned_question,
                answer=(
                    "I cannot help with requests to expose secrets, passwords, "
                    "or private credentials. Ask for a business action such as "
                    "creating a task or looking up a user."
                ),
            )

        if self._looks_like_task_creation(lowered):
            return self._create_task(cleaned_question, lowered, db)

        if self._looks_like_user_lookup(lowered):
            return self._lookup_user(cleaned_question, lowered, db)

        if self._looks_like_report_request(lowered):
            return self._generate_task_report(cleaned_question, db)

        return AskResponse(
            question=cleaned_question,
            answer=(
                "I can help with user lookups, task status reports, or creating "
                "a task in the real project database. Please include the user "
                "name or the task issue you want tracked."
            ),
        )

    def _is_unsafe_request(self, lowered: str) -> bool:
        blocked_terms = ("password", "secret", "api key", "token", "credential")
        return any(term in lowered for term in blocked_terms)

    def _looks_like_task_creation(self, lowered: str) -> bool:
        create_terms = ("create", "open", "raise", "assign")
        task_terms = ("ticket", "task", "issue", "incident", "request support", "broken")
        return any(term in lowered for term in create_terms) and any(
            term in lowered for term in task_terms
        )

    def _looks_like_user_lookup(self, lowered: str) -> bool:
        lookup_terms = ("employee", "user", "who is", "role", "profile", "email")
        return any(term in lowered for term in lookup_terms)

    def _looks_like_report_request(self, lowered: str) -> bool:
        report_terms = ("report", "summary", "count", "status", "overdue")
        return any(term in lowered for term in report_terms)

    def _create_task(self, question: str, lowered: str, db: Session) -> AskResponse:
        if len(question.split()) < 5:
            return AskResponse(
                question=question,
                answer=(
                    "I can create a task, but I need a short description of the "
                    "issue and the employee it should be assigned to."
                ),
                action=AssistantAction(name="create_task", status="needs_more_info"),
            )

        assignee = self._find_employee_from_question(lowered, db)
        if not assignee:
            return AskResponse(
                question=question,
                answer=(
                    "I can create the task, but I could not identify an employee "
                    "assignee from the real users table. Include an employee name "
                    "or email in the request."
                ),
                action=AssistantAction(name="create_task", status="needs_more_info"),
            )

        actor = self._get_automation_actor(db)
        if not actor:
            return AskResponse(
                question=question,
                answer=(
                    "I could not create a task because the database has no admin "
                    "or manager user to own the action."
                ),
                action=AssistantAction(name="create_task", status="failed"),
            )

        priority = (
            "high"
            if any(word in lowered for word in ("urgent", "down", "blocked", "critical"))
            else "medium"
        )
        payload = TaskCreate(
            title=question[:120],
            description=question,
            priority=priority,
            due_date=_utc_now() + timedelta(days=3),
            assigned_to_id=assignee.id,
        )
        task = TaskService.create_task(db=db, payload=payload, current_user=actor)

        return AskResponse(
            question=question,
            answer=(
                f"Created task #{task.id} for {assignee.name} with {priority} "
                f"priority. Status: {task.status}."
            ),
            action=AssistantAction(
                name="create_task",
                status="completed",
                data=self._task_to_dict(task),
            ),
        )

    def _lookup_user(self, question: str, lowered: str, db: Session) -> AskResponse:
        matches = self._find_users_from_question(lowered, db)

        if not matches:
            return AskResponse(
                question=question,
                answer=(
                    "I could not find a matching user in the real database. Try "
                    "a user name, email, or role that exists in this project."
                ),
                action=AssistantAction(name="fetch_user_information", status="not_found"),
            )

        user = matches[0]
        assigned_count = db.query(Task).filter(Task.assigned_to_id == user.id).count()
        created_count = db.query(Task).filter(Task.assigned_by_id == user.id).count()
        data = self._user_to_dict(user) | {
            "assigned_task_count": assigned_count,
            "created_task_count": created_count,
        }

        return AskResponse(
            question=question,
            answer=(
                f"{user.name} is a {user.role} user with email {user.email}. "
                f"They have {assigned_count} assigned tasks and created "
                f"{created_count} tasks."
            ),
            action=AssistantAction(
                name="fetch_user_information",
                status="completed",
                data=data,
            ),
        )

    def _generate_task_report(self, question: str, db: Session) -> AskResponse:
        total_tasks = db.query(Task).count()
        total_users = db.query(User).count()
        by_status = dict(
            db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        )
        by_priority = dict(
            db.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
        )
        by_role = dict(db.query(User.role, func.count(User.id)).group_by(User.role).all())
        overdue = (
            db.query(Task)
            .filter(Task.due_date < _utc_now(), Task.status != "completed")
            .count()
        )

        data = {
            "total_users": total_users,
            "users_by_role": by_role,
            "total_tasks": total_tasks,
            "tasks_by_status": by_status,
            "tasks_by_priority": by_priority,
            "overdue_open_tasks": overdue,
        }

        return AskResponse(
            question=question,
            answer=(
                f"Real database report: {total_users} users and {total_tasks} "
                f"tasks. Pending: {by_status.get('pending', 0)}; in progress: "
                f"{by_status.get('in-progress', 0)}; completed: "
                f"{by_status.get('completed', 0)}; overdue open tasks: {overdue}."
            ),
            action=AssistantAction(
                name="generate_task_report",
                status="completed",
                data=data,
            ),
        )

    def _find_employee_from_question(self, lowered: str, db: Session) -> User | None:
        users = db.query(User).filter(User.role == "employee").order_by(User.id.asc()).all()
        for user in users:
            if user.name.lower() in lowered or user.email.lower() in lowered:
                return user
        return users[0] if len(users) == 1 else None

    def _find_users_from_question(self, lowered: str, db: Session) -> list[User]:
        users = db.query(User).order_by(User.id.asc()).all()
        direct_matches = [
            user
            for user in users
            if user.name.lower() in lowered
            or user.email.lower() in lowered
        ]
        if direct_matches:
            return direct_matches

        return [user for user in users if user.role.lower() in lowered]

    def _get_automation_actor(self, db: Session) -> User | None:
        return (
            db.query(User)
            .filter(User.role.in_(("admin", "manager")))
            .order_by(User.id.asc())
            .first()
        )

    def _user_to_dict(self, user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def _task_to_dict(self, task: Task) -> dict[str, Any]:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat(),
            "assigned_to_id": task.assigned_to_id,
            "assigned_by_id": task.assigned_by_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }
