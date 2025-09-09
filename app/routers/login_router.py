import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

# PSS_HOST = "http://178.151.21.169:7000"            # for internet
# PSS_HOST = "http://172.17.0.1:7000"           # for docker default net
PSS_HOST = "http://pss_cont:7000"        # for docker mynet
    
          

def payload_from_token(request: Request):
    try:
        token = request.session.get("token", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])        
    except InvalidTokenError as e:
        raise credentials_exception
    else:
        return payload

def username_from_session(request: Request):
    try:
        token = request.session.get("token", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])        
    except InvalidTokenError as e:
        raise credentials_exception
    else:
        return payload.get("sub")


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    url = f"{PSS_HOST}/token"
    data = {
        "username": username,
        "password": password
    }
   
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
    if response.is_success:
        json = response.json()
        token = json["access_token"]
    else: 
        logger.error(f"Error. Response status_code: {response.status_code}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    # crate session
    request.session["token"] = token

    # redirect
    payload = payload_from_token(request)
    if payload.get("role") == "tutor":
        return RedirectResponse(url="/problemsets", status_code=302)
    else:
        return RedirectResponse(url="/problems", status_code=302)




# ===================================== get_token_payload ============================================

from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"} )

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


