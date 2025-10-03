import httpx, re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeaderSchema, ProblemSchema, AnswerSchema
from ..utils.utils import PSS_HOST, username_from_session
from sqlalchemy.orm import Session
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import ProblemSet, Ticket

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# логування
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------- List of problem headers (id, title, attr). AJAX

@router.get("/problems/lang/{lang}")
async def get_problem_headers(
    request: Request,
    lang: str,
):
    token = request.session.get("token", "")
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{PSS_HOST}/api/problems/lang/{lang}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        if response.is_success:
            # [{"id", "title", "attr"}]
            json = response.json()
            return json
        else:
            raise HTTPException(status_code=404, detail="Problems not found")


@router.get("/to_solve")
async def get_to_solve(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Показує студенту сторінку з задачами, розподіленими по задачникам.
    Враховуються лише відкриті та доступні поточному юзеру задачники.
    """
    username = username_from_session(request)
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    open_problemsets = [ps for ps in problemsets if ps.is_open() and re.match(ps.stud_filter, username)]

    token = request.session.get("token", "")
    if token == "":
        # redirect to login page
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "No token"
        })

    headers = {"Authorization": f"Bearer {token}"}
    psets = []
    for problemset in open_problemsets:
        pheaders = []
        for id in problemset.problem_ids.split():
            api_url = f"{PSS_HOST}/api/problems/{id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers)
                if response.is_success:
                    json = response.json()                    

                    problem_header = ProblemHeaderSchema(
                        id=json["id"], 
                        title=json["title"], 
                        attr=json["attr"])
                    pheaders.append(problem_header)

        rest_time: timedelta = problemset.open_time - \
            datetime.now() + timedelta(minutes=problemset.open_minutes)
        psets.append({
            "title": problemset.title,         #TODO  encode
            "username": problemset.username,
            "t": rest_time,
            "headers": pheaders})

    return templates.TemplateResponse("solving/to_solve.html", {"request": request, "psets": psets})


@router.get("/to_solve/problem/{prob_id}/{pset_title}")  
async def get_to_solve_problem(
    prob_id: str,
    pset_title: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Відкриває студенту вікно для вирішення задачі.
    Створює тікет і зберігає його в сесії, якщо це вже не зроблене раніше.
    """
    api_url = f"{PSS_HOST}/api/problems/{prob_id}"
    token = request.session.get("token", "")
    headers = {"Authorization": f"Bearer {token}"}

    # redirect to login page
    if token == "":
        return templates.TemplateResponse("login.html", {"request": request, "error": "No token"})

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
        json_obj = response.json()
    except Exception as e:
        err_mes = f"Error during a problem request: {e}"
        logger(err_mes)
        return RedirectResponse(url="/open_problems", status_code=302)
    
    username = username_from_session(request)

    ticket = db.query(Ticket).filter(Ticket.username == username and Ticket.problem_id == prob_id).first()
    # create a new ticket
    if ticket is None:
        problemset:ProblemSet = db.query(ProblemSet).get(pset_title)
        
        ticket = Ticket(
            username=username, 
            problem_id=prob_id, 
            records="",
            comment="",
            expire_time=problemset.exspire_time(),            
        )
        ticket.do_record("Вперше побачив задачу.", "User saw the task for the first time.");


        try:
            db.add(ticket)
            db.commit()
        except Exception as e:
            db.rollback()
            err_mes = f"Error during a ticket creating: {e}"
            logger(err_mes)
    
    # open a problem window
    problem = ProblemSchema(**json_obj)
    return templates.TemplateResponse(
        "solving/to_solve_problem.html",
        {"request": request, "problem": problem})

#-------------- check

@router.post("/check")
async def post_check(
    answer: AnswerSchema, 
    request: Request, 
    db: Session = Depends(get_db),
):
    """    AJAX
    Відправляє рішення задачі на перевірку до PSS і повертає відповідь від PSS.
    Додає в тіскет рішення і відповідь. 
    """
    # get a ticket
    username = username_from_session(request)
    ticket = db.query(Ticket).filter(Ticket.username == username and Ticket.problem_id == answer.id).first()
    if (ticket is None):
        raise RuntimeError("не знайдений тікет")
    if ticket.expire_time < datetime.now():
        return "Your time is over."

    api_url = f"{PSS_HOST}/api/check"
    data = {"id": answer.id, "solving": answer.solving}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=data)
        # state = response.status_code
        check_message = response.json()
    except Exception as e:
        err_mes = f"Error during a check solving: {e}"
        print(err_mes)
        return err_mes
  
    # write solving to the ticket
    ticket.do_record(answer.solving, check_message)
    db.commit()
    return check_message


