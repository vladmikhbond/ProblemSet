import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeader, ProblemSchema, AnswerSchema
from ..models.models import ProblemSet
from .. import dal as db
# from .login_router import PSS_HOST


# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/problemsets", summary="List of problemsets")
async def get_problemsets(request: Request):
    
    token = request.session.get("token", "")
    
    # return the login page with error message
    if token == "":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "No token"})
    
    problemsets: list[ProblemSet] = db.read_all_problemsets()
    if problemsets == None:
        raise HTTPException(status_code=404, detail="Error reading problemsets")

    problemsets = [pset for pset in problemsets if pset.user_id == "1Ivanenko" ]     
    return templates.TemplateResponse("problemset_list.html", {"request": request, "problemsets": problemsets})
 


# @router.get("/problem/{id}", summary="Get a problem.")
# async def get_probs(id: str, request: Request):
#     api_url = f"{PSS_HOST}/api/problems/{id}"
#     token = request.session.get("token", "")
#     headers = { "Authorization": f"Bearer {token}" }

#     if token == "":
#         # redirect to login page
#         return templates.TemplateResponse("login.html", {
#             "request": request, 
#             "error": "No token"
#         })
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(api_url, headers=headers)
#         json_obj = response.json()
#     except Exception as e:
#         err_mes = f"Error during a problem request: {e}"
#         logger.error(err_mes)
#         return RedirectResponse(url="/problems", status_code=302)
#     else:
#         problem = ProblemSchema(**json_obj) 
#         return templates.TemplateResponse(
#             "problem.html", 
#             {"request": request, "problem": problem} )


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
