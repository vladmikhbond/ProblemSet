from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .routers import login_router, problem_router, problemset_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Додаємо middleware для сесій
app.add_middleware(SessionMiddleware, secret_key="supersecret")

app.include_router(login_router.router, tags=["login"])
app.include_router(problem_router.router, tags=["problem"])
app.include_router(problemset_router.router, tags=["problemset"])



    

    


