import json, base64

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
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
    bs = bytes(ticket.track, encoding="utf-8")

    track64 = base64.b64encode(bs).decode()

    return templates.TemplateResponse("ticket/show.html", {
        "request": request, 
        "ticket": ticket,  
        "record": records[-1], 
        "track64": track64,
        "secondhand": "SECONDHAND" in ticket.records })
    

# -------------------------- report 

# @router.get("/ticket/report")
# async def get_ticket_report(
#     request: Request, 
#     db: Session = Depends(get_pss_db),
#     user: User=Depends(get_current_tutor)
# ):
#     """ 
#     Звіт
#     """
#     # define usernames
#     seances = get_filtered_problemsets(db, request)

#     set_of_usernames = set()
#     cell_values_dict: Dict[Tuple[str, int], float] = {} 

#     for seance in seances:
#         for ticket in seance.tickets:
#             set_of_usernames.add(ticket.username)
#             seance_questions = seance.get_questions(db)
#             cell_values_dict[ticket.username, seance.id] = result_from_ticket(ticket, seance_questions)[0]

#     usernames = sorted(user_filter(list(set_of_usernames), request))

#     # define cell values and sums
#     sums = {}
#     for username in usernames: 
#         row_values = [cell_values_dict.get((username, seance.id), 0)
#                        for seance in seances]
        
#         if   len(seances) == 0: sums[username] = 0
#         elif len(seances) == 1: sums[username] = sum(row_values)
#         else:                   sums[username] = round((sum(row_values) - min(row_values)) / (len(seances) - 1), 0)

         
#     return templates.TemplateResponse("ticket/report.html", {
#         "request": request, "seances": seances, "usernames": usernames, "dict": cell_values_dict, "sums": sums })

