import os
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.models import ProblemSet
from ..models.schemas import ProblemSetSchema

from .login_router import PSS_HOST, logger, get_current_user, AuthType

from ..dal import get_db  # Функція для отримання сесії БД
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Annotated

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

@router.get("/problemsets")
async def get_problemsets(
    request: Request, 
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
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
    
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    if problemsets == None:
        err_mes = "Error reading problemsets"
        logger.error(err_mes)
        raise HTTPException(status_code=404, detail=err_mes)

    problemsets = [pset for pset in problemsets if pset.user_id == "1Ivanenko" ]     
    return templates.TemplateResponse("problemset_list.html", {"request": request, "problemsets": problemsets})
 

@router.get("/problemset/{pset_id}")
async def edit_problemset_form(
    pset_id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    problemset = db.get(ProblemSet, pset_id)
    if not problemset:
        return RedirectResponse(url="/problemsets", status_code=302)
    return templates.TemplateResponse("problemset_edit.html", {"request": request, "problemset": problemset})

@router.post("/problemset/{pset_id}")
async def edit_problemset(
    pset_id: str,
    request: Request,
    user_id: str = Form(...),
    problem_ids: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(...),
    db: Session = Depends(get_db)
):
    problemset = db.get(ProblemSet, pset_id)
    if not problemset:
        return RedirectResponse(url="/problemsets", status_code=302)
    problemset.user_id = user_id
    problemset.problem_ids = problem_ids
    # open_time у форматі 'YYYY-MM-DDTHH:MM'
    problemset.open_time = datetime.strptime(open_time, "%Y-%m-%dT%H:%M")
    problemset.open_minutes = open_minutes
    db.commit()
    return RedirectResponse(url="/problemsets", status_code=302)










# @router.get("/problemset/{id}")
# async def get_problemset(id: str, request: Request):
#     """ 
#     Редагування обраного задачника поточного юзера (викладача).
#     """
#     token = request.session.get("token", "")
    
#     # return the login page with error message
#     if token == "":
#         return templates.TemplateResponse(
#             "login.html", 
#             {"request": request, "error": "No token"})
    
#     problemset: ProblemSet = db.read_problemset(id)
#     if problemset == None:
#         err_mes = "Error reading problemset"
#         logger.error(err_mes)
#         raise HTTPException(status_code=404, detail=err_mes)


#     return templates.TemplateResponse("problemset_edit.html", {"request": request, "problemset": problemset})

# @router.post("/problemset/{id}")
# async def post_problemset(problemset: ProblemSetSchema):
#     pass

