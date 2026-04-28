from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr
    source: str = Field(default="homepage", min_length=1, max_length=100)


class NewsletterSubscriberResponse(BaseModel):
    uuid: str
    email: str
    source: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NewsletterSubscribeResponse(BaseModel):
    subscriber: NewsletterSubscriberResponse
    already_subscribed: bool = False
