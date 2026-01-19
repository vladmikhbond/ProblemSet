from urllib.parse import unquote
import httpx
import os
import uuid

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .utils import get_filtered_problems

from .login_router import get_current_user, JUDGE
from ..models.models import Problem, User
from ..dal import get_pss_db  # Функція для отримання сесії БД

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------------------- list

@router.get("/problem/list")
async def get_problem_list(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
):
    problems = get_filtered_problems(db, request)
    return templates.TemplateResponse("problem/list.html", {"request": request, "problems": problems})

# ---------------------- new


@router.get("/problem/new")
async def get_problem_new(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
):
    """ 
    Створення нової задачі.
    """
    problem = Problem(
        id=str(uuid.uuid4()),
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
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
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
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
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
            id=str(uuid.uuid4()),
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
    
    payload = {"code": problem.code, "timeout": 2000}
    url = JUDGE[problem.lang]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

        check_message = response.text
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
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
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
        # Пропускаємо SQLAlchemy службові поля і PK
        if not key.startswith('_') and key != 'id'
    })
    return new_obj


# ------- del

@router.get("/problem/del/{id}")
async def get_problem_del(
    id: str,
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
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
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_user)
):
    problem = db.get(Problem, id)
    db.delete(problem)
    db.commit()
    return RedirectResponse(url="/problem/list", status_code=302)
