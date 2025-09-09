import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.pss_models import ProblemSet
from ..models.schemas import ProblemSetSchema

from .login_router import PSS_HOST, logger, payload_from_token

from ..dal import get_db  # Функція для отримання сесії БД
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
    role = payload.get("role")
    if role != "tutor":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": role})
        
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    # if problemsets == None:
    #     err_mes = "Error reading problemsets"
    #     logger.error(err_mes)
    #     raise HTTPException(status_code=404, detail=err_mes)
    username = payload.get("sub")
    problemsets = [p for p in problemsets if p.user_id == username ] 
    return templates.TemplateResponse("problemset_list.html", {"request": request, "problemsets": problemsets})

# ------- edit 

def dat2str(d): return d.strftime("%Y-%m-%dT%H:%M")

def str2dat(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M")


@router.get("/problemset/{id}")
async def edit_problemset_form(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Редагування обраного задачника поточного юзера (викладача).
    """
    problemset = db.get(ProblemSet, id)
    if not problemset:
        return RedirectResponse(url="/problemsets", status_code=302)
    return templates.TemplateResponse("problemset_edit.html", {"request": request, "problemset": problemset})


@router.post("/problemset/{id}")
async def edit_problemset(
    id: str,
    request: Request,
    user_id: str = Form(...),
    problem_ids: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(...),
    stud_filter: str = Form(...),
    db: Session = Depends(get_db)
):
    """ 
    Редагування обраного задачника поточного юзера (викладача).
    """
    problemset = db.get(ProblemSet, id)
    if not problemset:
        return RedirectResponse(url="/problemsets", status_code=302)
    problemset.user_id = user_id
    problemset.problem_ids = problem_ids
    problemset.open_time = str2dat(open_time)
    problemset.open_minutes = open_minutes
    problemset.stud_filter = stud_filter
    db.commit()
    return RedirectResponse(url="/problemsets", status_code=302)

# ------- new 

@router.get("/problemset")
async def new_problemset_form(
    request: Request,
    payload = Depends(payload_from_token), 
):
    """ 
    Створення нового задачника поточного юзера (викладача). 
    """
    problemset = ProblemSet(
        id = "",
        user_id = payload.get("sub"),                   
        problem_ids = "",                    
        open_time = str2dat(dat2str(datetime.now())),  # форматування now
        open_minutes = 0,
        stud_filter = ""
    )
    return templates.TemplateResponse("problemset_new.html", {"request": request, "problemset": problemset})


@router.post("/problemset")
async def new_problemset(
    request: Request,
    id: str = Form(...),
    user_id: str = Form(...),
    problem_ids: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(...),
    stud_filter: str = Form(...),
    db: Session = Depends(get_db)
):
    """ 
    Створення нового задачника поточного юзера (викладача).
    """
    problemset = ProblemSet(
        id = id,
        user_id = user_id,                   
        problem_ids = problem_ids,                    
        open_time = str2dat(open_time),
        open_minutes = open_minutes,
        stud_filter = stud_filter
    )
    try:
        db.add(problemset)                        
        db.commit()
    except Exception as e:
        err_mes = f"Error during a problem request: {e}"
        logger.error(err_mes)
        return templates.TemplateResponse("problemset_new.html", {"request": request, "problemset": problemset})
    return RedirectResponse(url="/problemsets", status_code=302)
    

# ------- del 

@router.get("/problemset/del/{id}")
async def problemset_del_form(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Видалення задачника - GET.
    """
    problemset = db.get(ProblemSet, id)
    if not problemset:
        return RedirectResponse(url="/problemsets", status_code=302)
    return templates.TemplateResponse("problemset_del.html", {"request": request, "problemset": problemset})


@router.post("/problemset/del/{id}")
async def problemset_del(
    id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """ 
    Видалення задачника - POST.
    """
    problemset = db.get(ProblemSet, id)
    db.delete(problemset)
    db.commit()
    return RedirectResponse(url="/problemsets", status_code=302)
