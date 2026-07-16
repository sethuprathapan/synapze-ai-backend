from sqlalchemy.orm import Session

from app.api.v1 import contact
from app.models.contact import Contact


class ContactService:

    @staticmethod
    def create_contact(db: Session, contact: contact.ContactRequest):

        # user = db.query(Contact).filter(Contact.email == contact.email).first()

        # if user:
        #     return {"message": "Contact already exists."}

        # new_contact = Contact(
        #     name=contact.name, email=contact.email, message=contact.message
        # )
        # db.add(new_contact)
        # db.commit()
        # db.refresh(new_contact)
        # return new_contact
        pass
