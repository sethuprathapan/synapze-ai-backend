from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.services.contact_service import ContactService
from app.schemas.common import ApiResponse
from app.schemas.contact import ContactRequest, ContactResponse

router = APIRouter(prefix="/contacts", tags=["Contact"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactRequest, db: Session = Depends(get_db)):
    db_contact = ContactService.create_contact(db=db, contact=contact)
    return ApiResponse(
        success=True,
        message="Contact message sent successfully",
        data=ContactResponse.model_validate(db_contact)
    )


@router.get("", response_model=ApiResponse, status_code=status.HTTP_200_OK)
def get_contacts(db: Session = Depends(get_db), contact: ContactRequest = None):
    db_contacts = ContactService.get_contacts(db=db, contact=contact)
    return ApiResponse(
        success=True,
        message="Contacts retrieved successfully",
        data=[ContactResponse.model_validate(contact) for contact in db_contacts]
    )