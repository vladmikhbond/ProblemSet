import re
from typing import List
from urllib.parse import unquote
from ..models.models import User, Problem

# ------------------------------------ PROBLEM_FILTER

PROBLEM_FILTER_KEY = "problemset_problem_filter"

def get_filtered_problems(db, request):
    """
    Повертає відфільтровані задачі.
    """
    problems = db.query(Problem).all()
    filter = unquote(request.cookies.get(PROBLEM_FILTER_KEY, "")).strip()
     
    if filter:
        problems = [p for p in problems if re.search(filter, p.attr, re.RegexFlag.U) is not None] 

    problems.sort(key=lambda p: p.attr+" "+p.title)
    return problems

# ------------------------------------ USER_FILTER

USER_FILTER_KEY = "problemset_user_filter"


# ------------------------------------ common 

def get_filtered_lines(lines: List[str], filtr_key, request):
    """
    Повертає відфільтровані рядки.
    """
    filter = unquote(request.cookies.get(filtr_key, ""))     
    if filter:
        lines = [line for line in lines if re.search(filter, line, re.RegexFlag.U) is not None] 
    return lines

