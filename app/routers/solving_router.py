
import httpx, re, json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_
from sqlalchemy.orm import Session

from .login_router import get_current_user, JUDGE
from ..models.schemas import AnswerSchema
from ..dal import get_pss_db  # Функція для отримання сесії БД
from ..models.models import Problem, ProblemSet, Ticket, User

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# логування
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------ list

@router.get("/solving")
async def get_solving_list(
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
):
    """
    Показує сторінку з задачами, розподіленими по задачникам.
    Враховуються лише відкриті та доступні поточному юзеру задачники.
    Послідовність здач в задачнику зберігається.
    """
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    open_problemsets = [
        ps for ps in problemsets 
        if ps.is_open and re.match(ps.stud_filter, user.username)]

    psets = []

    for problemset in open_problemsets:

        # get problems with the id in ids_list
        ids = problemset.get_problem_ids_list()
        problems = db.query(Problem).filter(Problem.id.in_(ids)).all()

        # sort problems as ordered identifiers in a list of identifiers
        dic = {p.id:p for p in problems}
        problems = [dic[id] for id in ids]

        # select unsolved problems only
        unsolved_problems = [
            p for p in problems
            if not any(
                t.username == user.username and t.state == 1
                for t in p.tickets
            )
        ]
        psets.append({
            "id": problemset.id,
            "title": problemset.title,
            "username": problemset.username,
            "rest": problemset.rest_time,
            "problems": unsolved_problems})
    
    # скільки задач вже вирішено
    problem_count = db.query(Ticket).filter(Ticket.username == user.username).filter(Ticket.state == 1).count()

    return templates.TemplateResponse("solving/list.html", 
            {"request": request, "psets": psets, "problem_count": problem_count})

# ---------------------------- open 

@router.get("/solving/problem/{problem_id}/{pset_id}")  
async def get_solving_problem(
    problem_id: str,
    pset_id: str,
    request: Request,
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
):
    """
    Відкриває вікно для вирішення задачі.
    Створює тікет і зберігає його в базі даних, якщо це вже не зроблене раніше.
    """  
    problem = db.get(Problem, problem_id)

    # get user's ticket
    ticket = db.query(Ticket) \
        .filter(and_(Ticket.username == user.username, Ticket.problem_id == problem_id)) \
        .first()

    # create a new ticket
    if ticket is None:
        problemset:ProblemSet = db.get(ProblemSet, pset_id) 
        ticket = Ticket(
            username=user.username, 
            problem_id=problem_id, 
            records="",
            expire_time=problemset.close_time,            
        )
        ticket.add_record("Вперше побачив задачу.", "User saw the task for the first time.");
        db.add(ticket)

    # find the old ticket
    else:
        # # show the ticket solving
        # records = ticket.get_records()
        # if len(records) > 1:
        #     problem.view = records[len(records)-1]["code"]
        ticket.add_record("Не вперше бачить задачу.", "SECONDHAND");
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a ticket creating: {e}"
        logger(err_mes)

    # open a problem window
    dict = {"py": "python", "js": "javascript", "cs": "csharp"}
    problem.lang = dict[problem.lang] 

    return templates.TemplateResponse("solving/problem.html", {"request": request, "problem": problem})

#-------------- check (AJAX)

@router.post("/check")
async def post_check(
    answer: AnswerSchema,
    db: Session = Depends(get_pss_db),
    user: User=Depends(get_current_user)
) -> str:
    """
    Відправляє рішення задачі на перевірку до judje і повертає відповідь .
    Додає в тіскет рішення і відповідь. 
    Приймає JSON у тілі у форматі AnswerSchema.
    """
    # get a ticket
    ticket = db.query(Ticket) \
        .filter(and_(Ticket.username == user.username, Ticket.problem_id == answer.problem_id)) \
        .first()
                              
    if ticket is None:
        raise RuntimeError("не знайдений тікет")
    if ticket.expire_time < datetime.now():
        return "Your time is over."

    problem = ticket.problem
    
    # Replace author's solving with user's one
    regex = regex_helper(problem.lang);
    if regex == None:
       return "Wrong Language" 

    # "\n" додається із-за C# директиви #line 1.
    user_code = re.sub(regex, "\n" + answer.solving, problem.code, count=1, flags=re.DOTALL)

    # Check user's solving
    payload = {"code": user_code, "timeout": 2000}
    url = JUDGE[problem.lang]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
        check_message = response.text
    except Exception as e:
        return f"Error. Is url '{url}' responding?"
  
    # Add solving to the ticket
    ticket.add_record(answer.solving, check_message)
    
    # Add trace to the ticket: 1) diffs from json, 2) add comment, 3) add to ticket
    diffs = json.loads(answer.trace)
    diffs.append([check_message[:10]])

    track = json.loads(ticket.track) if ticket.track else []
    track.extend(diffs)
    ticket.track =json.dumps(track)
     
    db.commit()
    return check_message

def regex_helper(lang:str):
    if lang == 'js' or lang == 'cs':
        return r"//BEGIN.*//END"
    elif lang == 'py':
        return r"#BEGIN.*#END"
    else:
        return None
