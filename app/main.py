from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .routers import login_router, problem_router, problemset_router

app = FastAPI()

# Додаємо middleware для сесій
app.add_middleware(SessionMiddleware, secret_key="supersecret")

app.include_router(login_router.router, tags=["login"])
app.include_router(problem_router.router, tags=["problem"])
app.include_router(problemset_router.router, tags=["problemset"])



    

    


