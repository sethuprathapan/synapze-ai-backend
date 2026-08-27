from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactRequest


class ContactService:

    @staticmethod
    def create_contact(db: Session, contact: ContactRequest) -> Contact:
        new_contact = Contact(
            name=contact.name,
            email=contact.email,
            message=contact.message,
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact

    @staticmethod
    def get_contacts(db: Session, name: str | None = None, email: str | None = None) -> list[Contact]:
        query = db.query(Contact)
        if name:
            query = query.filter(Contact.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(Contact.email.ilike(f"%{email}%"))
        return query.order_by(Contact.id.asc()).all()

