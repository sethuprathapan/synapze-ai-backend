from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.project import ProjectCreate, ProjectReplace, ProjectResponse, ProjectUpdate
from app.services.cache import task_cache

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(name=payload.name, description=payload.description, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ApiResponse(message="Project created", data=ProjectResponse.model_validate(project))


@router.get("", response_model=ApiResponse)
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.id.asc()).all()
    return ApiResponse(
        message="Projects retrieved",
        data=[ProjectResponse.model_validate(project) for project in projects],
    )


@router.get("/{project_id}", response_model=ApiResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, project_id, current_user.id)
    return ApiResponse(message="Project retrieved", data=ProjectResponse.model_validate(project))


@router.patch("/{project_id}", response_model=ApiResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, project_id, current_user.id)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field is required")
    for field, value in updates.items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ApiResponse(message="Project updated", data=ProjectResponse.model_validate(project))


@router.put("/{project_id}", response_model=ApiResponse)
def replace_project(
    project_id: int,
    payload: ProjectReplace,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, project_id, current_user.id)
    project.name = payload.name
    project.description = payload.description
    db.add(project)
    db.commit()
    db.refresh(project)
    return ApiResponse(message="Project replaced", data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", response_model=ApiResponse)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, project_id, current_user.id)
    db.delete(project)
    db.commit()
    task_cache.invalidate_owner(current_user.id)
    return ApiResponse(message="Project deleted", data=None)


def _owned_project(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project or project.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
