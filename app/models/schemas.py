from pydantic import BaseModel
from datetime import datetime

class ProblemHeader (BaseModel):
    id: str
    title: str
    attr: str
    

class ProblemSchema(BaseModel):
    id: str
    title: str
    attr: str
    lang: str
    cond: str
    view: str
    hint: str
    code: str
    author: str

    class Config:
        # orm_mode = True
        from_attributes=True

