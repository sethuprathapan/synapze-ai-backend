from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.enterprise_assistant import AskRequest, AskResponse
from app.services.enterprise_assistant_service import EnterpriseAssistantService

router = APIRouter()

assistant_service = EnterpriseAssistantService()


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    return assistant_service.ask(request.question, db)
