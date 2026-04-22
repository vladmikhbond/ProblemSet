from pydantic import BaseModel
from typing import List

class AnswerSchema(BaseModel):
    problem_id: str
    solving: str
    trace: str
    
    class Config:
        from_attributes=True

class ProblemSchema(BaseModel):
    id: str
    lang: str
    cond: str
    view: str
    seconds: int

    class Config:
        from_attributes=True

class HelpItem(BaseModel):
    head: str
    body: List[str]
