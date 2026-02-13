from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenData
from app.crud.user import get_user_by_email


# ⚡ ДЛЯ API-КЛИЕНТОВ (Bearer token)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",  # ✅ API-эндпоинт логина
    auto_error=False  # ✅ НЕ кидать 401 автоматически
)


async def get_current_user_from_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
) -> User:
    """Аутентификация для API-клиентов через Bearer token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user


# 🍪 ДЛЯ ВЕБ-ИНТЕРФЕЙСА (httpOnly cookie)
async def get_current_user_from_cookie(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Аутентификация для веб-интерфейса через cookie"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
    )

    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    token = token.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user


# ОБЩАЯ ПРОВЕРКА АКТИВНОСТИ (для обоих)
async def get_current_active_user(
    current_user: User = Depends(get_current_user_from_token),  # переопределим позже
) -> User:
    """Проверка, активен ли пользователь"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь неактивен"
        )
    return current_user


# Алиасы для удобства импорта
AuthUserFromToken = Annotated[User, Depends(get_current_user_from_token)]
AuthUserFromCookie = Annotated[User, Depends(get_current_user_from_cookie)]
ActiveUserFromToken = Annotated[User, Depends(get_current_active_user)]
ActiveUserFromCookie = Annotated[User, Depends(get_current_active_user)]
