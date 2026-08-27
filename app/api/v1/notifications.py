from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.notification import Notification
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=ApiResponse)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifications = (
        db.query(Notification)
        .join(Task)
        .join(Project)
        .filter(or_(Project.owner_id == current_user.id, Notification.user_id == current_user.id))
        .order_by(Notification.id.asc())
        .all()
    )
    return ApiResponse(
        message="Notifications retrieved",
        data=[NotificationResponse.model_validate(notification) for notification in notifications],
    )
