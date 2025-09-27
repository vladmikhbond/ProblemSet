from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .routers import login_router, problemset_router, solving_router, problem_router, ticket_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Додаємо middleware для сесій
app.add_middleware(SessionMiddleware, secret_key="supersecret")

app.include_router(login_router.router, tags=["login"])
app.include_router(solving_router.router, tags=["solving"])
app.include_router(problem_router.router, tags=["problem"])
app.include_router(problemset_router.router, tags=["problemset"])
app.include_router(ticket_router.router, tags=["ticket"])



    

    


