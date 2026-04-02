from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.schemas.token import TokenData

# Standard OAuth2 scheme for JWT token extraction
oauth2_extractor = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_extractor)]
) -> User:
    """
    Dependency that extracts the user from the JWT token and database.
    """
    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise unauthorized_error
    except JWTError:
        raise unauthorized_error
    
    # Query database for matching user
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise unauthorized_error
        
    return user

class RequiresRole:
    """
    Reusable dependency for controlling access based on user roles.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: '{user.role}' role lacks permission. Required: {self.allowed_roles}",
            )
        return user

# Custom Guard dependencies for route-level authorization
admin_required = Depends(RequiresRole(["admin"]))
analyst_required = Depends(RequiresRole(["analyst", "admin"]))

# Convenience dependency aliases for function parameters
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(RequiresRole(["admin"]))]
FinancialAnalyst = Annotated[User, Depends(RequiresRole(["analyst", "admin"]))]
AnyAuthenticatedUser = CurrentUser
