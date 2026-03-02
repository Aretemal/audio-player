from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_from_request, verify_auth_global
from app.auth.security import create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.crud.user import authenticate_user, create_user, get_user_by_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import RefreshTokenRequest, Token, UserCreate, UserLogin, UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        user = create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    response: Response,
    user_in: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    response.set_cookie(
        key=settings.COOKIE_ACCESS_TOKEN_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=settings.COOKIE_PATH,
        domain=settings.COOKIE_DOMAIN,
    )
    
    response.set_cookie(
        key=settings.COOKIE_REFRESH_TOKEN_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path=settings.COOKIE_PATH,
        domain=settings.COOKIE_DOMAIN,
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        },
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token_value = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_NAME)
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    
    try:
        payload = decode_token(refresh_token_value)
        token_type: str = payload.get("type")
        user_id_str: str = payload.get("sub")
        user_id: int = int(user_id_str)
        
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user = get_user_by_id(db, user_id=user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        response.set_cookie(
            key=settings.COOKIE_ACCESS_TOKEN_NAME,
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path=settings.COOKIE_PATH,
            domain=settings.COOKIE_DOMAIN,
        )
        
        response.set_cookie(
            key=settings.COOKIE_REFRESH_TOKEN_NAME,
            value=new_refresh_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path=settings.COOKIE_PATH,
            domain=settings.COOKIE_DOMAIN,
        )
        
        return {
            "message": "Token refreshed successfully",
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    response.delete_cookie(
        key=settings.COOKIE_ACCESS_TOKEN_NAME,
        path=settings.COOKIE_PATH,
        domain=settings.COOKIE_DOMAIN,
    )
    response.delete_cookie(
        key=settings.COOKIE_REFRESH_TOKEN_NAME,
        path=settings.COOKIE_PATH,
        domain=settings.COOKIE_DOMAIN,
    )
    return {"message": "Logout successful"}


@router.get(
    "/me",
    response_model=UserRead,
    dependencies=[Depends(verify_auth_global)],
)
def get_current_user_info(current_user: User = Depends(get_user_from_request)):
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    dependencies=[Depends(verify_auth_global)],
)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_user_from_request),
    db: Session = Depends(get_db),
):
    from app.crud.user import update_user
    
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return updated_user

