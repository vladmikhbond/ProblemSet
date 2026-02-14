import re
from typing import List
from urllib.parse import unquote
from datetime import datetime
from zoneinfo import ZoneInfo

from ..models.models import Problem

# -------------------- FILTERS

PROBLEM_FILTER_KEY = "problemset_problem_filter"
USER_FILTER_KEY = "problemset_user_filter"

def get_filtered_problems(db, request):
    """
    Повертає відфільтровані задачі з бази даних.
    """
    problems = db.query(Problem).all()
    filter = unquote(request.cookies.get(PROBLEM_FILTER_KEY, "")).strip()
     
    if filter:
        problems = [p for p in problems if re.search(filter, p.inline, re.RegexFlag.U) is not None] 

    problems.sort(key=lambda p: p.inline)
    return problems


def get_filtered_lines(lines: List[str], filter_key, request):
    """
    Повертає відфільтровані рядки.
    """
    filter = unquote(request.cookies.get(filter_key, ""))     
    if filter:
        lines = [line for line in lines if re.search(filter, line, re.RegexFlag.U) is not None] 
    return lines

#--------------------------------- time(UTC) <--> str(Kyiv) ------------------------  

FMT = "%Y-%m-%dT%H:%M"
ZONE = "Europe/Kyiv"

def time_to_str(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo(ZONE)).strftime(FMT)

def str_to_time(s: str) -> datetime:
    return datetime.strptime(s, FMT) \
        .replace(tzinfo=ZoneInfo(ZONE)) \
        .astimezone(ZoneInfo("UTC")) \
        .replace(tzinfo=None)

def delta_to_str(td):
    return f"{td.days} d {td.seconds//3600} h {(td.seconds//60)%60} m"
