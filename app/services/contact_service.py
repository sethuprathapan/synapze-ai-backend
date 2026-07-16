from sqlalchemy.orm import Session

from app.schemas.contact import ContactRequest
from app.models.contact import Contact


class ContactService:

    @staticmethod
    def create_contact(db: Session, contact: ContactRequest) -> Contact:
        new_contact = Contact(
            name=contact.name,
            email=contact.email,
            message=contact.message
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact

