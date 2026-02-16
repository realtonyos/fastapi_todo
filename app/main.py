import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.redis import init_redis, close_redis
from app.api.v1.endpoints import auth, users, tasks, web


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер жизненного цикла приложения.
    Выполняется один раз при старте и один раз при остановке.
    """
    logger.info("Starting up application...")

    try:
        redis_client = await init_redis()  # при старте инициализирует редис
        app.state.redis = redis_client  # сохраняет его в апп.стейт
        logger.info("Redis connected and ready to use")

    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        logger.error("Application cannot start without Redis. Exiting.")
        raise
    yield  # при остановке закрывает
    logger.info("🛑 Shutting down application...")
    try:
        await close_redis()
        logger.info("Redis connections closed successfully")

    except Exception as e:
        logger.error(f"Error while closing Redis: {e}")

    logger.info("Application shutdown complete")


app = FastAPI(
    title="FastAPI Todo",
    description="Todo API with FastAPI, Redis, Celery",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(web.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
