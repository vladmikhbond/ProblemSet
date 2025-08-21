import os
import logging
import httpx

from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..models.sessions import SessionData, backend, cookie, verifier


# логування
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()



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



@router.post("/create_session/{name}")
async def create_session(name: str, response: Response):

    session = uuid4()
    data = SessionData(username=name)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@router.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@router.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"