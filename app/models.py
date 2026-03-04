from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti        = Column(String(64),  primary_key=True, nullable=False)
    sub        = Column(String(128), nullable=True,  index=True)
    expires_at = Column(DateTime,    nullable=False,  index=True)
    revoked_at = Column(DateTime,    nullable=False,  server_default=func.now())
    reason     = Column(String(255), nullable=True)