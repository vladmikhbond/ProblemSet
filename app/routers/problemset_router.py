import re
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .login_router import get_current_user
from .problem_router import get_filtered_problems
from ..models.pss_models import Problem, ProblemSet, Ticket, User
from ..dal import get_pss_db  # Функція для отримання сесії БД
from sqlalchemy.orm import Session

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()
#--------------------------------- time <--> str ------------------------  

FMT = "%Y-%m-%dT%H:%M"
ZONE = "Europe/Kyiv"

def time_to_str(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo(ZONE)).strftime(FMT)

def str_to_time(s: str) -> datetime:
    return datetime.strptime(s, FMT) \
        .replace(tzinfo=ZoneInfo(ZONE)) \
        .astimezone(ZoneInfo("UTC"))


# ------- list 

@router.get("/problemset/list")
async def get_problemset_list(
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
):
    """ 
    Усі задачники поточного юзера (викладача).
    """
    all_problemsets: list[ProblemSet] = db.query(ProblemSet).all()

    problemsets = [p for p in all_problemsets if p.username == user.username ] 
    return templates.TemplateResponse("problemset/list.html", {"request": request, "problemsets": problemsets})

# ------- new 

@router.get("/problemset/new")
async def get_problemset_new(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
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

    problems = get_filtered_problems(request, db)
    return templates.TemplateResponse("problemset/edit.html", 
            {"request": request, "problemset": problemset, "problems": problems})


@router.post("/problemset/new")
async def post_problemset_new(
    request: Request,
    title: str = Form(...),
    # problem_ids: str = Form(...),
    open_time: str = Form(...),
    open_minutes: int = Form(0),
    stud_filter: str = Form(""),
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
):
    # читає з форми список обраних задач
    form = await request.form()
    prob_lst = form.getlist('prob')       #  "['id1', 'id2', 'id3']"
    prob_ids = '\n'.join(prob_lst)

    problems = get_filtered_problems(request, db)

    problemset = ProblemSet(
        title = title,
        username = user.username,
        problem_ids = prob_ids,                    
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
    user: User=Depends(get_current_user)
):
    """ 
    Редагування задачника.
    """
    problemset = db.get(ProblemSet, id)
    if user.username != problemset.username:
            raise HTTPException(401)

    problemset.open_time = time_to_str(problemset.open_time)
    problems = get_filtered_problems(request, db)

    arr = []
    for p in problems:
        p.checked = p.id in problemset.ids_list
        if p.checked:
            arr.append(p.inline) 
    problemset.problem_ids = "\n".join(arr)

    return templates.TemplateResponse("problemset/edit.html", 
            {"request": request, "problemset": problemset, "problems": problems})


@router.post("/problemset/edit/{id}")
async def post_problemset_edit(
    id: str,
    request: Request,
    open_time: str = Form(...),
    open_minutes: int = Form(0),
    stud_filter: str = Form(""),
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
):
    # читає з форми список обраних задач
    form = await request.form()
    prob_lst = form.getlist('prob')       #  "['id1', 'id2', 'id3']"
    prob_ids = '\n'.join(prob_lst)    

    # оновлює задачник
    problemset = db.get(ProblemSet, id) 
    problemset.problem_ids = prob_ids
    problemset.open_time = str_to_time(open_time)
    problemset.open_minutes = open_minutes
    problemset.stud_filter = stud_filter
    try:                       
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a problemset edit: {e}"
        print(err_mes)
        problems = get_filtered_problems(request, db)
        return templates.TemplateResponse("problemset/edit.html", 
                {"request": request, "problemset": problemset, "problems": problems})
    
    return RedirectResponse(url="/problemset/list", status_code=302)

# ------- del 

@router.get("/problemset/del/{id}")
async def get_problemset_del(
    id: str, 
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
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
    user: User=Depends(get_current_user)
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
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
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

