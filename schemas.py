from pydantic import BaseModel
from typing import Optional, List


class IdentifyRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None


class ContactResponse(BaseModel):
    primaryContatctId: int  # keeping the typo from the spec
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]


class IdentifyResponse(BaseModel):
    contact: ContactResponse
