from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, users, web
from app.api.v1.endpoints import tasks
# from app.core import templates


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web.router)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
