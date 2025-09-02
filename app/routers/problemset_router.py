import os
import logging
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.models import ProblemSet
from .. import dal as db
from .login_router import PSS_HOST, logger


# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/problemsets")
async def get_problemsets(request: Request):
    """ 
    Усі задачники поточного юзера (викладача).
    """
    #TODO: define the current user

    token = request.session.get("token", "")
    
    # return the login page with error message
    if token == "":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "No token"})
    
    problemsets: list[ProblemSet] = db.read_all_problemsets()
    if problemsets == None:
        err_mes = "Error reading problemsets"
        logger.error(err_mes)
        raise HTTPException(status_code=404, detail=err_mes)

    problemsets = [pset for pset in problemsets if pset.user_id == "1Ivanenko" ]     
    return templates.TemplateResponse("problemset_list.html", {"request": request, "problemsets": problemsets})
 


@router.get("/problemset/{id}", summary="Get a problemset.")
async def get_problemset(id: str, request: Request):
    """ 
    Редагування обраного задачника поточного юзера (викладача).
    """
    token = request.session.get("token", "")
    
    # return the login page with error message
    if token == "":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "No token"})
    
    problemset: ProblemSet = db.read_problemset(id)
    if problemset == None:
        err_mes = "Error reading problemset"
        logger.error(err_mes)
        raise HTTPException(status_code=404, detail=err_mes)

    problemsets = [pset for pset in problemsets if pset.user_id == "1Ivanenko" ]     #TODO:
    return templates.TemplateResponse("problemset_edit.html", {"request": request, "problemsets": problemsets})


# @router.post("/check", summary="Check the answer to the problem")
# async def post_check(answer: AnswerSchema):
#     """
#     Виймає рішення з відповіді, відправляє його на перевірку до PSS і повертає відповідь від PSS   
#     """
#     api_url = f"{PSS_HOST}/api/check"
#     data = { "id": answer.id, "solving": answer.solving }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(api_url, json=data)
#         # state = response.status_code
#         json = response.json()
#     except Exception as e:
#         err_mes = f"Error during a check solving: {e}"
#         logger.error(err_mes)
#         return err_mes
#     else:
#         return json
