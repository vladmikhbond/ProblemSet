from urllib.parse import unquote
import httpx, os, uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .login_router import get_current_tutor
from ..models.pss_models import Problem, User
from ..utils.utils import PSS_HOST
from ..dal import get_db  # Функція для отримання сесії БД

PROBLEM_FILTER_KEY = "problemset_problem_filter";

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------------------- auxiliary tools
#  
def filtered_problems(request: Request, db: Session) -> list[Problem]:
    """ 
    Профільтровані і впорядклвані задачі.
    """
    filter = unquote(request.cookies.get(PROBLEM_FILTER_KEY, "")).strip()
    probs = db.query(Problem)
    if filter:
        probs = probs.filter(or_(Problem.attr.contains(filter), Problem.title.contains(filter))
                             ).order_by(Problem.attr, Problem.title)
    return probs.all()


# ----------------------------------- list

@router.get("/problem/list")
async def get_problem_list(
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    problems = filtered_problems(request, db)
    return templates.TemplateResponse("problem/list.html", {"request": request, "problems": problems})

# ---------------------- new

@router.get("/problem/new")
async def get_problem_new( 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Створення нової задачі.
    """
    problem = Problem(
        id = str(uuid.uuid4()),
        author=user.username,
        timestamp=datetime.now(),
        title="", attr="", lang="js", cond="", view="", hint="", code="", 
    )
    return templates.TemplateResponse("problem/edit.html", {"request": request, "problem": problem})

# ----------------------- edit 

@router.get("/problem/edit/{id}")
async def get_problem_edit(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Редагування задачі.
    """
    problem = db.get(Problem, id)
    if not problem:
        return RedirectResponse(url="/problem/list", status_code=302)
    return templates.TemplateResponse("problem/edit.html", {"request": request, "problem": problem})


@router.post("/problem/edit/{id}")
async def post_problem_edit(
    id: str,
    request: Request,
    title: str = Form(...),
    attr: str = Form(...),
    lang: str = Form(...),
    cond: str = Form(...),
    view: str = Form(...),
    hint: str = Form(""),
    code: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Редагування задачі.
    Оновити екземпляр задачі даними з форми і перевірити авторське рішення.
    """
    problem = db.get(Problem, id)
    is_new = len(id) > 32 and not problem
    # нова задача
    if is_new:
        problem = Problem(
            id = str(uuid.uuid4()),
        )
    problem.title = title
    problem.attr = attr
    problem.lang = lang
    problem.cond = cond
    problem.view = view
    problem.hint = hint
    problem.code = code
    problem.author = author    
    problem.timestamp = datetime.now()

    # check author's solving

    data = {"source": problem.code, "lang": problem.lang}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{PSS_HOST}/api/proof", json=data)
        check_message = response.json()
        if not check_message.startswith("OK"):
            return templates.TemplateResponse("problem/edit.html", {"request": request, "problem": problem, "error": check_message})
    except Exception as e:
        err_mes = f"Помилка при перевірці рішення задачі: {e}"
        return templates.TemplateResponse("problem/edit.html", {"request": request, "problem": problem, "error": err_mes})
    
    # save changes in DB
    if is_new:
        db.add(problem)
    db.commit()
    
    return RedirectResponse(url="/problem/list", status_code=302)

# ---------------------- copy 

@router.get("/problem/copy/{id}")
async def get_problem_copy(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Копіювання задачі.
    """
    old_problem = db.get(Problem, id)
    if not old_problem:
        return PlainTextResponse("Не знайдений оригінал задачі.")
        
    new_problem = copy_instance(old_problem)
    new_problem.id = str(uuid.uuid4()) 
    new_problem.title += " - Copy"
    db.add(new_problem)                              
    db.commit()

    return templates.TemplateResponse("problem/edit.html", 
            {"request": request, "problem": new_problem})


def copy_instance(obj):
    cls = obj.__class__
    new_obj = cls(**{
        key: value for key, value in obj.__dict__.items()
        if not key.startswith('_') and key != 'id'  # Пропускаємо SQLAlchemy службові поля і PK
    })
    return new_obj


# ------- del 

@router.get("/problem/del/{id}")
async def get_problem_del(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Видалення задачі.
    """
    problem = db.get(Problem, id)
    if not problem:
        return RedirectResponse(url="/problemset/list", status_code=302)
    return templates.TemplateResponse("problem/del.html", {"request": request, "problem": problem})


@router.post("/problem/del/{id}")
async def post_problem_del(
    id: str,
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    problem = db.get(Problem, id)
    db.delete(problem)
    db.commit()
    return RedirectResponse(url="/problem/list", status_code=302)



# --------------- List of problem headers. AJAX

@router.get("/problem/lang/{lang}")
async def get_problem_headers(
    request: Request,
    lang: str,
):
    token = request.cookies["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{PSS_HOST}/api/problems/lang/{lang}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        if response.is_success:
            # headers: [{"id", "title", "attr"}]
            headers = response.json()
            filter = unquote(request.cookies.get(PROBLEM_FILTER_KEY, ""))
            headers = [h for h in headers if filter in h["title"] or filter in h["attr"]] 
            return headers
        else:
            raise HTTPException(status_code=404, detail="Problems not found")

