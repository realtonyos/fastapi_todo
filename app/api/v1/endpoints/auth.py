from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, Token
from app.crud.user import get_user_by_email, create_user
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.templates import templates
from app.models.user import User


router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    description="""
    Регистрация пользователя, сначала проверяем, создан ли пользователь,
    Если да, то вывод ошибки, если нет, то создаем нового пользователя в ДБ
    """,
)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    user = await get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже создан"
        )
    user = await create_user(db=db, user_in=user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    description="""
    Авторизация пользователя.
    1. Проверяем по email. 2. Проверяем пароль
    Если все успешно, создаем токен
    """,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")
