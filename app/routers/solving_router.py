import os
import re
import httpx
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeaderSchema, ProblemSchema, AnswerSchema
from ..utils.utils import PSS_HOST, delta2str, username_from_session
from sqlalchemy.orm import Session
from ..dal import get_db, writedown_to_ticket  # Функція для отримання сесії БД
from ..models.pss_models import ProblemSet, Ticket

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# логування
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/problems/lang/{lang}", summary="List of problem headers (id, title, attr). AJAX")
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
            return {}     # TODO


@router.get("/problems/active")
async def get_problems_active(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Показує студенту сторінку з задачами, розподіленими по відкритим задачникам.
    """
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    open_problemsets = [ps for ps in problemsets if ps.is_open()]

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
                        id=json["id"], title=json["title"], attr=json["attr"])
                    pheaders.append(problem_header)

        rest_time: timedelta = problemset.open_time - \
            datetime.now() + timedelta(minutes=problemset.open_minutes)
        psets.append({
            "id": problemset.title,
            "username": problemset.username,
            "rest_time": delta2str(rest_time),
            "headers": pheaders})

    return templates.TemplateResponse("problems_active.html", {"request": request, "psets": psets})


@router.get("/to_solve/{prob_id}")
async def get_problem(
    prob_id: str,
    request: Request
):
    """
    Відкриває студенту вікно для вирішення задачі.
    Отримує тікет і зберігає його в сесії, якщо це вже не зроблене раніше.
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
    else:
        # create a new ticket
        username = username_from_session(request)
        writedown_to_ticket(username, prob_id)

        # open a problem window
        problem = ProblemSchema(**json_obj)
        return templates.TemplateResponse(
            "problem.html",
            {"request": request, "problem": problem})


@router.post("/check")
async def post_check(answer: AnswerSchema, request: Request):
    """    AJAX
    Відправляє рішення задачі на перевірку до PSS і повертає відповідь від PSS.
    Додає в тіскет рішення і відповідь. 
    """
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
    else:
        # append a ticket
        username = username_from_session(request)
        writedown_to_ticket(username, answer.id, answer.solving, check_message)

        return check_message


# ------- show problem  -- 
# TODO перенести

@router.get("/problem/show/{id}")
async def get_problem_show(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Показ вирішень з одного тікету - GET.
    """
    RE_TEMPLATE = r"~0~(.*?)~1~(.*?)~2~(.*?)~3~"
    ticket = db.get(Ticket, id)
    matches = re.findall(RE_TEMPLATE, ticket.records, flags=re.S)
    records = [{"when": m[2], "code":m[0].strip(), "check":m[1].strip()} for m in matches]

    return templates.TemplateResponse("problem_show.html", 
            {"request": request, "ticket": ticket, "records": records})
