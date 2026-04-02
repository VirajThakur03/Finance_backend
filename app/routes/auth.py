import logging
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.core import security
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Type aliases for cleaner dependencies
Database = Annotated[AsyncSession, Depends(get_session)]

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Database
) -> User:
    """
    Creates a new user account with a secure hashed password.
    """
    logger.info(f"Attempting to register new user: {user_data.email}")
    
    # Verify email uniqueness
    existing_user_stmt = select(User).where(User.email == user_data.email)
    existing_user = (await db.execute(existing_user_stmt)).scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"Registration failed: Email {user_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    new_user = User(
        email=user_data.email,
        hashed_password=security.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    db.add(new_user)
    await db.flush() # Populate ID before commit if needed
    
    logger.info(f"Successfully registered user: {new_user.email} (ID: {new_user.id})")
    return new_user

@router.post("/login", response_model=Token)
async def login(
    db: Database,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    Authenticates a user and returns a Bearer JWT token.
    """
    logger.info(f"Login attempt for user: {credentials.username}")
    
    user_stmt = select(User).where(User.email == credentials.username)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    
    if not user or not security.verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Failed login for: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for User ID: {user.id}")
    return Token(access_token=token, token_type="bearer")
