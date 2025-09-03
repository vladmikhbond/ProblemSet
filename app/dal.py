import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
from .models.models import ProblemSet

engine = create_engine(f"sqlite:////data/PSS.db", echo=True)

def get_db():
    return Session(engine)

# def read_all_problemsets() -> list[ProblemSet] | None:
#     try:
#         with Session(engine) as session:
#             problemsets = session.query(ProblemSet).all()
#         return problemsets    
#     except SQLAlchemyError as e:
#         return None


# def read_problemset(id:str) -> ProblemSet | None:
#     try:
#         with Session(engine) as session:
#             problemset = session.get(ProblemSet, id)
#         return problemset    
#     except SQLAlchemyError as e:
#         return None


   

