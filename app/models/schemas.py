from pydantic import BaseModel

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

    class Config:
        from_attributes=True
