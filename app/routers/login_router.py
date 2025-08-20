from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import logging
import httpx

# налаштуємо логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # url = "http://localhost:7000/token"
    url = "http://172.17.0.1:7000/token"
    
    
    data = {
        "username": username,
        "password": password
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
        json = response.json()
        print(json)
        
    except Exception as e:
        logger.error(f"Error during login request: {e}")
        return {
            "status_code": 500,
            "response": {"error": "Internal server error"}
        }

    return {
        "status_code": response.status_code,
        "response": response.json()
    }
    # if username == "admin" and password == "secret":
    #     return HTMLResponse("Login successful!")
    # else:
    #     return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


from pydantic import BaseModel

class SessionData(BaseModel):
    username: str
    token: str

###

from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

cookie_params = CookieParameters()

### Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

###

from uuid import UUID
from fastapi_sessions.backends.implementations import InMemoryBackend

backend = InMemoryBackend[UUID, SessionData]()