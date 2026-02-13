# FastAPI Todo — Production-ready pet project

# Стек
- FastAPI + SQLAlchemy 2.0 (async)
- PostgreSQL + asyncpg
- Redis (Celery broker + cache)
- Celery + Flower
- JWT + httpOnly cookies
- Docker + Docker Compose

# Фичи
- Регистрация/логин (JWT + cookies)
- CRUD задач с проверкой владельца
- Веб-интерфейс (Bootstrap 5)
- Фоновые задачи (Celery + Redis)
- Docker-изоляция


## 📦 Установка
```bash
git clone <your-repo>
cd fastapi-todo
cp .env.example .env
docker compose up --build