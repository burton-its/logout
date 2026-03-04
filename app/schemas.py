from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# raw JWT string
# for example -> "logout", "password_change"
class RevokeRequest(BaseModel):
    token: str                        
    reason: Optional[str] = None      


class RevokeResponse(BaseModel):
    jti: str
    revoked_at: datetime
    message: str


class ValidateResponse(BaseModel):
    jti: str
    is_revoked: bool
    reason: Optional[str] = None
    revoked_at: Optional[datetime] = None


class CleanupResponse(BaseModel):
    deleted_count: int
    message: str