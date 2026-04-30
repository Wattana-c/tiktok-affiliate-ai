from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccountBase(BaseModel):
    platform: str
    account_name: str
    access_token: str
    is_active: Optional[bool] = True
    rate_limit: Optional[int] = 5

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    platform: Optional[str] = None
    account_name: Optional[str] = None
    access_token: Optional[str] = None
    is_active: Optional[bool] = None
    rate_limit: Optional[int] = None

class Account(AccountBase):
    id: int
    failed_attempts: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
