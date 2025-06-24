from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "TU_SECRETO"
ALGORITHM = "HS256"

def crear_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)