import logging  # для логирования ошибок

from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings


logger = logging.getLogger(__name__)

# Изначально None, потому что клиент будет создан при старте приложения
redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Возвращает экземпляр Redis-клиента.
    Если клиент еще не создан, выбрасывает исключение.
    Эта функция будет использоваться в эндпоинтах для получения доступа к Redis.
    """
    if redis_client is None:
        # Если мы оказались здесь, значит клиент не был инициализирован при старте
        logger.error("Redis client not initialized. Did you forget to call init_redis?")
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def init_redis() -> Redis:
    """
    Создает подключение к Redis.
    Вызывается один раз при старте приложения (в lifespan).
    """
    global redis_client
    redis_cache_url = settings.REDIS_URL.replace("/0", "/1")
    logger.info(f"Connecting to Redis cache at {redis_cache_url}")

    #    - ConnectionPool управляет несколькими соединениями
    #    - from_url создает пул из URL-строки
    #    - max_connections=10 — максимум одновременных соединений
    pool = ConnectionPool.from_url(
        redis_cache_url,
        max_connections=10,
        decode_responses=False  # Оставляем False, потому что будем хранить JSON
    )
    redis_client = Redis.from_pool(pool)
    try:
        await redis_client.ping()
        logger.info("Successfully connected to Redis and ping successful")
    except Exception as e:
        logger.error(f"Failed to ping Redis: {e}")
        # Если не можем подключиться к Redis, лучше упасть сразу, чем работать без кеша
        raise RuntimeError(f"Redis connection failed: {e}")

    return redis_client


async def close_redis() -> None:
    """
    Закрывает все соединения с Redis.
    Вызывается один раз при остановке приложения.
    """
    global redis_client

    if redis_client is None:
        logger.warning("Redis client not initialized, nothing to close")
        return

    logger.info("Closing Redis connections...")
    try:
        await redis_client.close()
        logger.info("Redis connections closed successfully")
    except Exception as e:
        logger.error(f"Error while closing Redis connections: {e}")
    finally:
        redis_client = None
