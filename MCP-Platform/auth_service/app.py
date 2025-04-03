from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
import redis
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json

app = FastAPI(title="Authentication Service")

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("MEMORY_URL", "redis://memory:6379").split("://")[1].split(":")[0],
    port=6379,
    decode_responses=True
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: List[str] = ["user"]

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []

# Mock user database - in production, use a real database
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin"),
        "disabled": False,
        "roles": ["admin", "user"]
    },
    "analyst": {
        "username": "analyst",
        "full_name": "Security Analyst",
        "email": "analyst@example.com",
        "hashed_password": pwd_context.hash("analyst"),
        "disabled": False,
        "roles": ["analyst", "user"]
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": pwd_context.hash("user"),
        "disabled": False,
        "roles": ["user"]
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, roles=payload.get("roles", []))
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def has_role(required_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        user_roles = set(current_user.roles)
        required_role_set = set(required_roles)
        if not user_roles.intersection(required_role_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "roles": user.roles},
        expires_delta=access_token_expires
    )
    
    # Store token in Redis for potential revocation
    redis_client.set(
        f"token:{access_token}",
        json.dumps({"username": user.username, "roles": user.roles}),
        ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/roles")
async def read_user_roles(current_user: User = Depends(get_current_active_user)):
    return {"roles": current_user.roles}

@app.post("/users", response_model=User)
async def create_user(
    user: User,
    password: str,
    current_user: User = Depends(has_role(["admin"]))
):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    
    # In a real application, save to a database
    fake_users_db[user.username] = user_dict
    
    return User(**user_dict)

@app.get("/users", response_model=List[User])
async def list_users(current_user: User = Depends(has_role(["admin"]))):
    users = []
    for username, user_dict in fake_users_db.items():
        user_data = {k: v for k, v in user_dict.items() if k != "hashed_password"}
        users.append(User(**user_data))
    return users

@app.post("/revoke")
async def revoke_token(
    token: str,
    current_user: User = Depends(has_role(["admin"]))
):
    # In a real application, you would validate the token first
    redis_client.delete(f"token:{token}")
    return {"message": "Token revoked successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 