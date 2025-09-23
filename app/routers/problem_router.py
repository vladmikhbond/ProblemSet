import httpx, os, uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.pss_models import Problem, ProblemSet, Ticket
from ..models.schemas import ProblemHeaderSchema, ProblemSetSchema
from ..utils.utils import payload_from_token,str2dat, dat2str, PSS_HOST
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



# # ------- copy 

# @router.get("/problem/copy/{id}")
# async def get_problem_copy(
#     id: str, 
#     request: Request, 
#     db: Session = Depends(get_db)
# ):
#     """ 
#     Копіювання задачі.
#     """
#     old_problem = db.get(Problem, id)
#     if not old_problem:
#         return RedirectResponse(url="/problem/list", status_code=302)
    
#     new_problem = copy_instance(old_problem)
#     new_problem.id = str(uuid())
#     new_problem.title += " - Copy"
#     db.add(new_problem)                              
#     db.commit()

#     return templates.TemplateResponse("problem/problem_edit.html", 
#             {"request": request, "problem": new_problem})


# from sqlalchemy.orm import make_transient

# def copy_instance(obj):
#     cls = obj.__class__
#     new_obj = cls(**{
#         key: value for key, value in obj.__dict__.items()
#         if not key.startswith('_') and key != 'id'  # Пропускаємо SQLAlchemy службові поля і PK
#     })
#     return new_obj




# # ------- new 

# @router.get("/problemset/new")
# async def new_problemset_form(
#     request: Request,
#     payload = Depends(payload_from_token), 
# ):
#     """ 
#     Створення нового задачника поточного юзера (викладача). 
#     """
#     problemset = ProblemSet(
#         title = "",
#         username = payload.get("sub"),                   
#         problem_ids = "",                    
#         open_time = str2dat(dat2str(datetime.now())),  # форматування now
#         open_minutes = 0,
#         stud_filter = ""
#     )
#     return templates.TemplateResponse("problemset/problemset_new.html", {"request": request, "problemset": problemset})


# @router.post("/problemset/new")
# async def new_problemset(
#     request: Request,
#     title: str = Form(...),
#     username: str = Form(...),
#     problem_ids: str = Form(...),
#     open_time: str = Form(...),
#     open_minutes: int = Form(...),
#     stud_filter: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     """ 
#     Створення нового задачника поточного юзера (викладача).
#     """
#     problemset = ProblemSet(
#         title = title,
#         username = username,                   
#         problem_ids = problem_ids,                    
#         open_time = str2dat(open_time),
#         open_minutes = open_minutes,
#         stud_filter = stud_filter
#     )
#     try:
#         db.add(problemset)                        
#         db.commit()
#     except Exception as e:
#         err_mes = f"Error during a problem request: {e}"
#         print(err_mes)
#         return templates.TemplateResponse("problemset/problemset_new.html", {"request": request, "problemset": problemset})
#     return RedirectResponse(url="/problemset/list", status_code=302)


# # ------- del 

# @router.get("/problemset/del/{id}")
# async def problemset_del_form(
#     id: str, 
#     request: Request, 
#     db: Session = Depends(get_db)
# ):
#     """ 
#     Видалення задачника - GET.
#     """
#     problemset = db.get(ProblemSet, id)
#     if not problemset:
#         return RedirectResponse(url="/problemset/list", status_code=302)
#     return templates.TemplateResponse("problemset/problemset_del.html", {"request": request, "problemset": problemset})


# @router.post("/problemset/del/{id}")
# async def problemset_del(
#     id: str,
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     """ 
#     Видалення задачника - POST.
#     """
#     problemset = db.get(ProblemSet, id)
#     db.delete(problemset)
#     db.commit()
#     return RedirectResponse(url="/problemset/list", status_code=302)

# # ------- show 

# @router.get("/problemset/show/{id}")
# async def problemset_show(
#     id: str, 
#     request: Request, 
#     db: Session = Depends(get_db)
# ):
#     """ 
#     Показ результатів - GET.
#     """
#     problemset = db.get(ProblemSet, id)
#     problem_ids = problemset.problem_ids.split()
#     dict = {}
#     for problem_id in problem_ids:
#         problem = db.get(Problem, problem_id)
#         dict[problem_id] = problem

#     return templates.TemplateResponse("problemset/problemset_show.html", {"request": request, "problemset": problemset, "dict": dict})

