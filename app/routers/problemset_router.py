import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.pss_models import Problem, ProblemSet, Ticket
from ..utils.utils import payload_from_token
from ..dal import get_db  # Функція для отримання сесії БД
from sqlalchemy.orm import Session

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/problemset/list")
async def get_problemset_list(
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
        
    all_problemsets: list[ProblemSet] = db.query(ProblemSet).all()

    username = payload.get("sub")
    problemsets = [p for p in all_problemsets if p.username == username ] 
    return templates.TemplateResponse("problemset/list.html", {"request": request, "problemsets": problemsets})

# ------- new 

@router.get("/problemset/new")
async def get_problemset_new(
    request: Request,
):
    """ 
    Створення нового задачника поточного юзера (викладача). 
    """
    now_str = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%dT%H:%M")
    problemset = ProblemSet(
        title = "",                
        problem_ids = "",                    
        open_time = now_str,  
        open_minutes = 0,
        stud_filter = ""
    )
    return templates.TemplateResponse("problemset/new.html", {"request": request, "problemset": problemset})


@router.post("/problemset/new")
async def post_problemset_new(
    request: Request,
    title: str = Form(...),
    problem_ids: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(...),
    stud_filter: str = Form(...),
    db: Session = Depends(get_db),
    payload = Depends(payload_from_token), 
):
    """ 
    Створення нового задачника поточного юзера (викладача).
    """

    dt = datetime.strptime(open_time, "%Y-%m-%dT%H:%M")
    dt = dt.replace(tzinfo=ZoneInfo("Europe/Kyiv")).astimezone(ZoneInfo("UTC"))

    problemset = ProblemSet(
        title = title,
        username = payload.get("sub"),                    
        problem_ids = problem_ids,                    
        open_time = dt,
        open_minutes = open_minutes,
        stud_filter = stud_filter
    )
    try:
        db.add(problemset)                        
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a problem request: {e}"
        print(err_mes)
        return templates.TemplateResponse("problemset/new.html", {"request": request, "problemset": problemset})
    return RedirectResponse(url="/problemset/list", status_code=302)


# ------- edit 

@router.get("/problemset/edit/{id}")
async def get_problemset_edit(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Редагування обраного задачника поточного юзера (викладача).
    """
    problemset = db.get(ProblemSet, id)
    problem_headers = []

    if not problemset:
        return RedirectResponse(url="/problemset/list", status_code=302)
    
    dt_str = problemset.open_time.astimezone(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%dT%H:%M")
    problemset.open_time = dt_str
    return templates.TemplateResponse("problemset/edit.html", 
            {"request": request, "problemset": problemset, "problem_headers": problem_headers})


@router.post("/problemset/edit/{id}")
async def post_problemset_edit(
    id: str,
    request: Request,
    username: str = Form(...),  # from hidden input
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
        return RedirectResponse(url="/problemset/list", status_code=302)
    problemset.username = username  
    problemset.problem_ids = problem_ids

    dt = datetime.strptime(open_time, "%Y-%m-%dT%H:%M")
    dt = dt.replace(tzinfo=ZoneInfo("Europe/Kyiv")).astimezone(ZoneInfo("UTC"))

    problemset.open_time = dt
    problemset.open_minutes = open_minutes
    problemset.stud_filter = stud_filter
    try:                       
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a problemset edit: {e}"
        print(err_mes)
        return templates.TemplateResponse("problemset/edit.html", {"request": request, "problemset": problemset})
    
    return RedirectResponse(url="/problemset/list", status_code=302)

# ------- del 

@router.get("/problemset/del/{id}")
async def get_problemset_del(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Видалення задачника.
    """
    problemset = db.get(ProblemSet, id)
    if not problemset:
        return RedirectResponse(url="/problemset/list", status_code=302)
    return templates.TemplateResponse("problemset/del.html", {"request": request, "problemset": problemset})


@router.post("/problemset/del/{id}")
async def post_problemset_del(
    id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """ 
    Видалення задачника.
    """
    problemset = db.get(ProblemSet, id)
    db.delete(problemset)
    db.commit()
    return RedirectResponse(url="/problemset/list", status_code=302)

# ------- show 

@router.get("/problemset/show/{id}")
async def problemset_show(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Показ вирішень з одного задачника.
    """
    problemset = db.get(ProblemSet, id)
    problem_ids = problemset.problem_ids.split()
    dict = {}
    for problem_id in problem_ids:
        problem = db.get(Problem, problem_id)
        dict[problem_id] = problem

    return templates.TemplateResponse("problemset/show.html", {"request": request, "problemset": problemset, "dict": dict})

