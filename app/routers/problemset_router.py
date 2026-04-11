from datetime import datetime
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .utils import delta_to_str, str_to_time, time_to_str
from .utils import USER_FILTER_KEY, get_filtered_lines, get_filtered_problemsets, get_filtered_problems, get_filtered_and_marked_problems
from .login_router import get_current_tutor
from ..models.models import Problem, ProblemSet, User
from ..dal import get_pss_db  # Функція для отримання сесії БД


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ------- list 

@router.get("/problemset/list")
async def get_problemset_list(
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Усі задачники поточного юзера (викладача).
    """
    all_problemsets = get_filtered_problemsets(db, request)

    problemsets = [p for p in all_problemsets if p.username == user.username ] 
    problemsets.sort(key=lambda p: p.title)
    for p in problemsets: 
        p.open_time_as_str = time_to_str(p.open_time).replace("T", " ")
        if p.is_open:
            p.open_minutes_as_str = f"{p.open_minutes} m"
            p.rest_time_as_str = delta_to_str(p.rest_time)
        else: 
            p.open_minutes_as_str = "-"
            p.rest_time_as_str = "-"
        p.problems_count = len(p.get_problem_ids_list())

    return templates.TemplateResponse(request, "problemset/list.html", {"problemsets": problemsets})


# ------- new 

@router.get("/problemset/new")
async def get_problemset_new(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Створення нового задачника поточного юзера (викладача). 
    """
    problemset = ProblemSet(
        title = "",
        username = user.username,      
        problem_ids = "",                    
        open_time = time_to_str(datetime.now()),  
        open_minutes=20,
        stud_filter = "",
    )
    
    problems = get_filtered_and_marked_problems(db, request)

    return templates.TemplateResponse(request, "problemset/edit.html", {"problemset": problemset, "problems": problems})

@router.post("/problemset/new")
async def post_problemset_new(
    request: Request,
    title: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(0),
    stud_filter: str = Form(""),
    problem_ids: str = Form(""),
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):

    problemset = ProblemSet(
        id = str(uuid.uuid4()),
        title = title,
        username = user.username,
        problem_ids = problem_ids,                    
        open_time = str_to_time(open_time),
        open_minutes = open_minutes,
        stud_filter = stud_filter
    )
    
    try:
        db.add(problemset)                        
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a problem request: {e}"

        problems = get_filtered_and_marked_problems(db, request)
        return templates.TemplateResponse(request, "problemset/edit.html", 
            {"problemset": problemset, "problems": problems, "err_mes": err_mes})
    
    return RedirectResponse(url="/problemset/list", status_code=302)


# ------- edit 

@router.get("/problemset/edit/{id}")
async def get_problemset_edit(
    id: str, 
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Редагування задачника.
    """
    problemset = db.get(ProblemSet, id)
    
    # only the owner can edit it
    if user.username != problemset.username:
        raise HTTPException(403)

    problemset.open_time = time_to_str(problemset.open_time)
    filtered_problems = get_filtered_and_marked_problems(db, request)

    # set checkboxes of the problems
    problem_ids_list = problemset.get_problem_ids_list()  
    for p in filtered_problems:
        p.checked = p.id in problem_ids_list

    return templates.TemplateResponse(request, "problemset/edit.html", {"problemset": problemset, "problems": filtered_problems})


@router.post("/problemset/edit/{id}")
async def post_problemset_edit(
    request: Request,
    id: str,
    title: str = Form("noname"),
    open_time: str = Form(...),
    open_minutes: int = Form(0),
    stud_filter: str = Form(""),
    problem_ids: str = Form(...),
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
): 

    # оновлює задачник
    problemset = db.get(ProblemSet, id)

    problemset.title = title 
    problemset.set_problem_ids(problem_ids)
    problemset.open_time = str_to_time(open_time)
    problemset.open_minutes = open_minutes
    problemset.stud_filter = stud_filter
    problemset.problem_ids = problem_ids
    try:                       
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a problemset edit: {e}"
        print(err_mes)
        problems = get_filtered_and_marked_problems(db, request)
        return templates.TemplateResponse(request, "problemset/edit.html", {"problemset": problemset, "problems": problems})
    
    return RedirectResponse(url="/problemset/list", status_code=302)

# ------- del 

@router.get("/problemset/del/{id}")
async def get_problemset_del(
    id: str, 
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Видалення задачника.
    """
    problemset = db.get(ProblemSet, id)
    if not problemset:
        return RedirectResponse(url="/problemset/list", status_code=302)
    return templates.TemplateResponse(request, "problemset/del.html", {"problemset": problemset})


@router.post("/problemset/del/{id}")
async def post_problemset_del(
    id: str,
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Видалення задачника.
    """
    problemset = db.get(ProblemSet, id)
    db.delete(problemset)
    db.commit()
    return RedirectResponse(url="/problemset/list", status_code=302)

# ------- show solvings

@router.get("/problemset/show/{id}")
async def problemset_show(
    id: str, 
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Показ вирішень з одного задачника.
    """
    problemset = db.get(ProblemSet, id)

    problem_ids = problemset.get_problem_ids_list()
    dict = {}
    
    for problem_id in problem_ids:
        problem = db.get(Problem, problem_id)
        dict[problem_id] = problem
        # filter
        usernames = [t.username for t in problem.tickets]
        filtered_usernames = get_filtered_lines(usernames, USER_FILTER_KEY, request)
        tickets = [*filter(lambda t: t.username in filtered_usernames, problem.tickets)]
        for t in tickets: 
            t.str = time_to_str(t.when_success()) if t.state == 1 else ""
        problem.tickets = tickets
        # sort
        problem.tickets.sort(key = lambda t: t.when_success())

    return templates.TemplateResponse(request, "problemset/show.html", {"problemset": problemset, "dict": dict})

