import datetime
import base64

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from .login_router import get_current_tutor
from ..dal import get_pss_db  # Функція для отримання сесії БД
from ..models.models import Ticket, User
from .utils import USER_FILTER_KEY, get_filtered_problemsets

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ------- del


@router.get("/ticket/del/{id}/{pset_title}")
async def get_ticket_del(
    id: str,
    pset_title: str,
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Видалення тікету.
    """
    ticket = db.get(Ticket, id)
    if not ticket:
        return "No ticket to delete."
    return templates.TemplateResponse(request, "ticket/del.html", {"ticket": ticket, "pset_title": pset_title})


@router.post("/ticket/del/{id}/{pset_id}")
async def post_ticket_del(
    id: str,
    pset_id: str,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Видалення тікету.
    """
    ticket = db.get(Ticket, id)
    db.delete(ticket)
    db.commit()
    return RedirectResponse(url=f"/problemset/show/{pset_id}", status_code=302)


# ------- show

@router.get("/ticket/anime/{id}")
async def get_ticket_anime(
    id: str,
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Показ  з одного тікету.
    """
    ticket = db.get(Ticket, id)
    records = ticket.get_records()
    bs = bytes(ticket.track, encoding="utf-8")

    track64 = base64.b64encode(bs).decode()

    return templates.TemplateResponse(request, "ticket/show.html", {
        "ticket": ticket,
        "record0": records[0],
        "record": records[-1],
        "track64": track64})


# -------------------------- report

@router.get("/ticket/report")
async def get_ticket_report(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Рахує кількість розв'язаних задач для кожного користувача.
    """
    groups = (
        db.query(Ticket.username, func.count(Ticket.id))
        .filter(Ticket.state == 1)
        .group_by(Ticket.username)
        .all()
    )
    groups.sort(key=lambda g: -g[1])

    return templates.TemplateResponse(request, "ticket/report.html", {"groups": groups},
    )


# -------------------------- статистика по вирішенням

@router.get("/ticket/statistics")
async def get_ticket_statitics(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Рахує довжину трас 
    """
    count = 0
    sum_trace_len = 0
    sum_code_len = 0
    sum_time_tick = 0

    tickets = db.query(Ticket).filter(Ticket.state == 1).all()
    for t in tickets:
        if not t.track or t.track[0] != '[':
            continue
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        if t.when_success() < start_date:
            continue
        count += 1
        sum_trace_len += len(t.track)
        c = t.get_records()[-1]["code"]
        sum_code_len += len(c)
        ticks = t.track.count('[') - 1
        sum_time_tick += ticks
     
    return {
        "Кількість вирішень": count,
        "Середній розмір треку": sum_trace_len//count, 
        "Сер. розмір коду вирішення": sum_code_len//count, 
        "Сер. кількість тактів часу": sum_time_tick//count, 
        }
