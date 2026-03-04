from jose import jwt
import uuid, time

secret = "cs361dog"
alg = "HS256"

payload = {
    "sub": "1",
    "email": "test@example.com",
    "jti": str(uuid.uuid4()),
    "iat": int(time.time()),
    "exp": int(time.time()) + 900
}

token = jwt.encode(payload, secret, algorithm=alg)
print(token)