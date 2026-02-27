from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(String, default="primary")  # "primary" or "secondary"
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)
