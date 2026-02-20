from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .utils import delta_to_str, get_filtered_lines, USER_FILTER_KEY, str_to_time, time_to_str
from .login_router import get_current_tutor
from .problem_router import get_filtered_problems
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
    all_problemsets: list[ProblemSet] = db.query(ProblemSet).all()

    problemsets = [p for p in all_problemsets if p.username == user.username ] 
    for p in problemsets: 
        p.open_time_as_str = time_to_str(p.open_time).replace("T", " ")
        if p.open_minutes:
            p.open_minutes_as_str = f"{p.open_minutes} m"
            p.rest_time_as_str = delta_to_str(p.rest_time)
        else: 
            p.open_minutes_as_str = "-"
            p.rest_time_as_str = "-"

    return templates.TemplateResponse("problemset/list.html", {"request": request, "problemsets": problemsets})

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

    problems = get_filtered_problems(db, request)
    
    return templates.TemplateResponse("problemset/edit.html", 
            {"request": request, "problemset": problemset, "problems": problems})


@router.post("/problemset/new")
async def post_problemset_new(
    request: Request,
    title: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(0),
    stud_filter: str = Form(""),
    problem_ids: str = Form(...),
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    problems = get_filtered_problems(db, request)

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
        return templates.TemplateResponse("problemset/edit.html", 
                {"request": request, "problemset": problemset, "problems": problems, "err_mes": err_mes})
    
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
    filtered_problems = get_filtered_problems(db, request)

    # set checkboxes of the problems
    problem_ids_list = problemset.get_problem_ids_list()  
    for p in filtered_problems:
        p.checked = p.id in problem_ids_list

    return templates.TemplateResponse("problemset/edit.html", 
            {"request": request, "problemset": problemset, "problems": filtered_problems})


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
        problems = get_filtered_problems(db, request)
        return templates.TemplateResponse("problemset/edit.html", 
                {"request": request, "problemset": problemset, "problems": problems})
    
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
    return templates.TemplateResponse("problemset/del.html", {"request": request, "problemset": problemset})


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
        usernames = [un for un in get_filtered_lines(usernames, USER_FILTER_KEY, request)]
        problem.tickets = [t for t in problem.tickets if t.username in usernames]
        # sort
        problem.tickets.sort(key = lambda t: t.when_success())

    return templates.TemplateResponse("problemset/show.html", {"request": request, "problemset": problemset, "dict": dict})

