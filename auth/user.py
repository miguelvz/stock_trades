from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = SECRET_KEY

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, username):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, minutes=60),
            "iat": datetime.utcnow(),
            "sub": username
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=ALGORITHM
        )
    
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[ALGORITHM])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials=Security(security)):
        return self.decode_token(auth.credentials)



