import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .login_router import get_current_tutor
from ..dal import get_pss_db  # Функція для отримання сесії БД
from ..models.models import Ticket, User

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# логування
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------- show

@router.get("/ticket/show/{id}")
async def get_solving_ticket(
    id: str, 
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Показ вирішень з одного тікету.
    """
    ticket = db.get(Ticket, id)
    records = ticket.get_records()
    return templates.TemplateResponse("ticket/show.html", 
            {"request": request, "ticket": ticket,  "records": records})

# ------- del 

@router.get("/ticket/del/{id}/{pset_title}")
async def get_ticket_del(
    id: str, 
    pset_title: str, 
    request: Request, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Видалення тікету.
    """
    ticket = db.get(Ticket, id)
    if not ticket:
        return "No ticket to delete."
    return templates.TemplateResponse("ticket/del.html", 
            {"request": request, "ticket": ticket, "pset_title": pset_title})


@router.post("/ticket/del/{id}/{pset_id}")
async def post_ticket_del(
    id: str,
    pset_id: str, 
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Видалення тікету.
    """
    ticket = db.get(Ticket, id)
    db.delete(ticket)
    db.commit()
    return RedirectResponse(url=f"/problemset/show/{pset_id}", status_code=302)

