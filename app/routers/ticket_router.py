import re

from fastapi import APIRouter, Depends, Request, Response, Form
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



@router.get("/ticket/show/{id}")
async def get_solving_ticket(
    id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """ 
    Показ вирішень з одного тікету.
    """
    RE_TEMPLATE = r"~0~(.*?)~1~(.*?)~2~(.*?)~3~"
    ticket = db.get(Ticket, id)
    matches = re.findall(RE_TEMPLATE, ticket.records, flags=re.S)
    records = [{"when": m[2], "code":m[0].strip(), "check":m[1].strip()} for m in matches]

    return templates.TemplateResponse("problemset/ticket_show.html", 
            {"request": request, "ticket": ticket, "records": records})
