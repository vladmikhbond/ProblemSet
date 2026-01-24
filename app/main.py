import os, jwt
from fastapi import FastAPI
from .routers import login_router, problemset_router, solving_router, problem_router, ticket_router
from fastapi.staticfiles import StaticFiles
from .models.models import User


for var in ("SECRET_KEY", "ALGORITHM", "TOKEN_LIFETIME", "TOKEN_URL"):
    if os.getenv(var) is None:
        raise RuntimeError(f"Environment variable {var} is not set.")

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.middleware("http")
async def attach_current_user(request, call_next):
    """Attach current user (if any) to request.state.user by decoding access_token cookie."""
    token = request.cookies.get("access_token")
    request.state.user = None
    if token:
        try:
            payload = jwt.decode(token, login_router.SECRET_KEY, algorithms=[login_router.ALGORITHM])
            request.state.user = User(username=payload.get("sub"), role=payload.get("role"))
        except Exception:
            request.state.user = None
    response = await call_next(request)
    return response
    
app.include_router(login_router.router, tags=["login"])
app.include_router(solving_router.router, tags=["solving"])
app.include_router(problem_router.router, tags=["problem"])
app.include_router(problemset_router.router, tags=["problemset"])
app.include_router(ticket_router.router, tags=["ticket"])



    

    


