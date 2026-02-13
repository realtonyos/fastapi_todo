from fastapi import APIRouter

from app.schemas.user import UserOut
from app.api.deps import ActiveUserFromToken

router = APIRouter()


@router.get(
    "/me",
    response_model=UserOut,
    description="Получить информацию о текущем пользователе")
async def read_users_me(
    current_user: ActiveUserFromToken,
):
    return current_user
