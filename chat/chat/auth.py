from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User
from .schemas import UserCreate, UserLogin
from .db import get_db
from pydantic import BaseSettings

auth_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


class Settings(BaseSettings):
    authjwt_secret_key: str = "ab86a1227b4b04ea4ba54d16aef059f3ef456975c052994a508898c5fab195d4" # random generated string   | 
    authjwt_access_token_expires: int = 3600  # 1 hour
    authjwt_refresh_token_expires: int = 86400  # 24 hours
    authjwt_header_name: str = "Authorization"
    authjwt_header_type: str = "Bearer"


@AuthJWT.load_config
def get_config():
    return Settings()


@auth_router.post('/register')
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return JSONResponse(content={"message": "User created successfully"}, status_code=201)

@auth_router.post('/login')
async def login(user: UserLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create access and refresh tokens
    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@auth_router.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    try:
        # Refreshing token requires jwt_refresh
        Authorize.jwt_refresh_token_required()

        # Get the current user and generate a new access token
        current_user = Authorize.get_jwt_subject()
        new_access_token = Authorize.create_access_token(subject=current_user)

        return {"access_token": new_access_token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
