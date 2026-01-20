import re
from typing import List
from urllib.parse import unquote
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

