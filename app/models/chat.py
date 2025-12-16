from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
