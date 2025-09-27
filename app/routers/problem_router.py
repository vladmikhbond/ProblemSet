import httpx, os, uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.pss_models import Problem, ProblemSet, Ticket
from ..models.schemas import ProblemHeaderSchema, ProblemSetSchema
from ..utils.utils import payload_from_token, str2dat, dat2str, PSS_HOST
from ..dal import get_db  # Функція для отримання сесії БД
from sqlalchemy.orm import Session, noload


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# логування
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/problem/list")
async def get_problem_list(
    request: Request, 
    db: Session = Depends(get_db),
    payload = Depends(payload_from_token),
):
    """ 
    Усі задачі поточного юзера (викладача).
    """
    # return the login page with error message
    role = payload.get("role")
    if role != "tutor":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": role})
    
    username = payload.get("sub")
    problems: list[Problem] = sorted(
        db.query(Problem).filter(Problem.author == username).all(), 
        key=lambda p: p.attr)

    return templates.TemplateResponse("problem/list.html", {"request": request, "problems": problems})

# ------- edit 

@router.get("/problem/edit/{id}")
async def get_problem_edit(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
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
    hint: str = Form(...),
    code: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db),
):
    """ 
     Редагування задачі.
     Оновити екземпляр задачі даними з форми. Перевірити код.
    """
    problem = db.get(Problem, id)
    if not problem:
        return RedirectResponse(url="/problem/list", status_code=302)
    problem.title = title
    problem.attr = attr
    problem.lang = lang
    problem.cond = cond
    problem.view = view
    problem.hint = hint
    problem.code = code
    problem.author = author    
    problem.timestamp = datetime.now()

    api_url = f"{PSS_HOST}/api/proof"
    data = {"source": problem.code, "lang": problem.lang}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=data)
        check_message = response.json()
        if not check_message.startswith("OK"):
            return templates.TemplateResponse("problem/edit.html", {"request": request, "problem": problem, "error": check_message})
    except Exception as e:
        err_mes = f"Error during a check solving: {e}"
        logger.error(err_mes)
        return templates.TemplateResponse("problem/edit.html", {"request": request, "problem": problem, "error": err_mes})
    db.commit()
    return RedirectResponse(url="/problem/list", status_code=302)



# ------- copy 

@router.get("/problem/copy/{id}")
async def get_problem_copy(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
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


from sqlalchemy.orm import make_transient

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
    db: Session = Depends(get_db)
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
    request: Request,
    db: Session = Depends(get_db)
):
    """ 
    Видалення задачі.
    """
    problem = db.get(Problem, id)
    db.delete(problem)
    db.commit()
    return RedirectResponse(url="/problem/list", status_code=302)



