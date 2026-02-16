from typing import Annotated

from fastapi import Form, APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from app.db.session import get_db
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.templates import templates
from app.crud.task import get_tasks
from app.models.user import User
from app.api.deps import get_current_user_from_cookie
from app.schemas.task import TaskCreate, TaskUpdate
from app.crud.task import create_task, get_task, delete_task, update_task
from app.celery.email import send_welcome_email


router = APIRouter(tags=["web"])


@router.get("/register", include_in_schema=False)
async def register_form(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )


@router.get("/login", include_in_schema=False)
async def login_form(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


@router.post("/register-web", include_in_schema=False)
async def register_web(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Проверить, есть ли пользователь
    user = await get_user_by_email(db, email)
    if user:
        # Вернуть форму с ошибкой
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Пользователь уже существует"}
        )

    # 2. Создать пользователя
    user_in = UserCreate(email=email, password=password)
    user = await create_user(db, user_in)

    # 2.1 Celery отправка сообщения
    send_welcome_email.delay(email)

    # 3. Редирект на логин
    response = RedirectResponse(url="/login?registered=1", status_code=302)
    return response


@router.post("/login-web", include_in_schema=False)
async def login_web(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Найти пользователя
    user = await get_user_by_email(db, email)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный email или пароль"}
        )

    # 2. Проверить пароль
    if not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный email или пароль"}
        )

    # 3. Создать токен
    access_token = create_access_token(data={"sub": user.email})

    # 4. Установить куки и редирект
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    return response


@router.get("/dashboard", include_in_schema=False)
async def dashboard(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: User = Depends(get_current_user_from_cookie),  # ЯВНО
    skip: int = 0,
    limit: int = 100
):
    """Веб-интерфейс: список задач текущего пользователя"""
    tasks = await get_tasks(
        request=request,
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return templates.TemplateResponse(
        "tasks/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "tasks": tasks
        }
    )


@router.get("/tasks/create", include_in_schema=False)
async def create_task_form(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Форма создания задачи"""
    return templates.TemplateResponse(
        "tasks/create.html",
        {"request": request, "user": current_user}
    )


@router.post("/tasks/create", include_in_schema=False)
async def create_task_web(
    title: str = Form(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Создание задачи через веб-форму"""
    task_in = TaskCreate(title=title, description=description)
    await create_task(db, task_in, current_user.id)
    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/tasks/{task_id}/delete", include_in_schema=False)
async def delete_task_web(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Удаление задачи через веб"""
    task = await get_task(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=403)
    await delete_task(db, task_id)
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/tasks/{task_id}/edit", include_in_schema=False)
async def edit_task_form(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Форма редактирования задачи"""
    # 1. Получаем задачу
    task = await get_task(db, task_id)

    # 2. Проверяем существование и владельца
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # 3. Рендерим форму
    return templates.TemplateResponse(
        "tasks/edit.html",
        {
            "request": request,
            "user": current_user,
            "task": task
        }
    )


@router.post("/tasks/{task_id}/edit", include_in_schema=False)
async def edit_task_web(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(None),
    completed: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Сохранение изменений задачи"""
    # 1. Получаем задачу
    task = await get_task(db, task_id)

    # 2. Проверяем существование и владельца
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # 3. Обновляем задачу
    task_in = TaskUpdate(
        title=title,
        description=description if description else None,
        completed=completed
    )
    await update_task(db, task, task_in)

    # 4. Редирект обратно на дашборд
    return RedirectResponse(url="/dashboard", status_code=302)