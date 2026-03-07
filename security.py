import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from config import JWT_SECRET, JWT_ALG, ACCESS_TOKEN_EXPIRE_SECONDS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, email: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)

    payload = {
        "sub":   str(user_id),
        "email": email,
        "jti":   str(uuid.uuid4()),   # updated here
        "iat":   int(now.timestamp()),
        "exp":   int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)