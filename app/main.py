from fastapi import FastAPI
from .routers import login_router
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Додаємо middleware для сесій
app.add_middleware(SessionMiddleware, secret_key="supersecret")

app.include_router(login_router.router, tags=["problem"])


