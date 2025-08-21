from pydantic import BaseModel
from datetime import datetime

class ProblemHeader (BaseModel):
    id: str
    title: str
    attr: str
    

   
