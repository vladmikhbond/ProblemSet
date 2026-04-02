import re
from typing import List
from urllib.parse import unquote
from datetime import datetime
from zoneinfo import ZoneInfo

from ..models.models import Problem, ProblemSet

# -------------------- FILTERS

WORKBOOK_FILTER_KEY = "problemset_workbook_filter"
PROBLEM_FILTER_KEY = "problemset_problem_filter"
USER_FILTER_KEY = "problemset_user_filter"

def get_filtered_problemsets(db, request):
    """
    Повертає відфільтровані і впорядковані задачники з бази даних.
    """
    problemsets = db.query(ProblemSet).all()

    filter = unquote(request.cookies.get(WORKBOOK_FILTER_KEY, "")).strip()

    if filter:
        try:
            pattern = re.compile(filter, re.UNICODE)
            problemsets = [ p for p in problemsets if p.title and pattern.search(p.title) ]
        except re.error:
            # Invalid regex — ignore filter or log error
            pass 

    problemsets.sort(key=lambda p: p.title)
    return problemsets


def get_filtered_problems(db, request):
    """
    Повертає відфільтровані задачі з бази даних.
    Структура виразу фільтрації: [re_фільтру]...[str_фільтру_за_умовою]
    """
    problems = db.query(Problem).all()
    filter = unquote(request.cookies.get(PROBLEM_FILTER_KEY, "")).strip()

    if filter:
        # split filter value
        arr = filter.split("...")
        filter_by_cond = ""
        if len(arr) == 2:
            filter = arr[0].strip()
            filter_by_cond = arr[1].strip().lower()
        
        # filter
        try:
            pattern = re.compile(filter, re.UNICODE)
            problems = [ p for p in problems if p.attr and pattern.search(p.attr) ]
        except re.error:
            # Invalid regex — ignore filter or log error
            pass 
        
        if filter_by_cond:
            problems = [p for p in problems if filter_by_cond in p.cond.lower()] 

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
