import datetime as dt
import uuid
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
from .models.models import ProblemSet

engine = create_engine(f"sqlite:////data/TSS2.db", echo=True)

def read_all_problesets() -> list[ProblemSet] | None:
    try:
        with Session(engine) as session:
            problemsets = session.query(ProblemSet).all()
        return problemsets    
    except SQLAlchemyError as e:
        # logging.error(f"Error adding problem '{user.username}': {e}")
        return None


   

