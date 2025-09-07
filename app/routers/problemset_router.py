import os
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.pss_models import ProblemSet
from ..models.schemas import ProblemSetSchema

from .login_router import PSS_HOST, logger, payload_from_token

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
    payload = Depends(payload_from_token),
):
    """ 
    Усі задачники поточного юзера (викладача).
    """
    # return the login page with error message
    if payload.get("role") != "tutor":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": payload[1]})
    
    
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    if problemsets == None:
        err_mes = "Error reading problemsets"
        logger.error(err_mes)
        raise HTTPException(status_code=404, detail=err_mes)
    username = payload.get("sub")
    # open_problemsets = [pset for pset in problemsets if pset.user_id == username ]   
    return templates.TemplateResponse("problemset_list.html", {"request": request, "problemsets": problemsets})
 

@router.get("/problemset/{pset_id}")
async def edit_problemset_form(
    pset_id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Редагування обраного задачника поточного юзера (викладача).
    """
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
    """ 
    Редагування обраного задачника поточного юзера (викладача).
    """
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
