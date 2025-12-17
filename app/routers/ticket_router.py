import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .login_router import get_current_tutor
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import Ticket, User

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# логування
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@router.get("/ticket/show/{id}")
async def get_solving_ticket(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Показ вирішень з одного тікету.
    """
    REGEX = r"~0~(.*?)~1~(.*?)~2~(.*?)~3~"
    ticket = db.get(Ticket, id)
    matches = re.findall(REGEX, ticket.records, flags=re.S)
    records = [{"when": m[2], "code":m[0].strip(), "check":m[1].strip()} for m in matches]

    return templates.TemplateResponse("ticket/show.html", 
            {"request": request, "ticket": ticket,  "records": records})

# ------- del 

@router.get("/ticket/del/{id}/{pset_title}")
async def get_ticket_del(
    id: str, 
    pset_title: str, 
    request: Request, 
    db: Session = Depends(get_db),
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


@router.post("/ticket/del/{id}/{pset_title}")
async def post_ticket_del(
    id: str,
    pset_title: str, 
    db: Session = Depends(get_db),
    user: User=Depends(get_current_tutor)
):
    """ 
    Видалення тікету.
    """
    ticket = db.get(Ticket, id)
    db.delete(ticket)
    db.commit()
    return RedirectResponse(url=f"/problemset/show/{pset_title}", status_code=302)

