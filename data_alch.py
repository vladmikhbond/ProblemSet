import datetime as dt
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .models.models import Problem, User
from sqlalchemy.inspection import inspect 
import logging
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

engine = create_engine(f"sqlite:////data/TSS2.db", echo=True)

# ===================== Users ======================

def read_all_users() -> list[User]:
    with Session(engine) as session:
        users = session.query(User).all()
    return users


def add_user(user: User) -> User|None:
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password
    try:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user) 
        return user
    except SQLAlchemyError as e:
        logging.error(f"Error adding problem '{user.username}': {e}")
        return None


def read_user(username: str) -> User|None:
    try:
        with Session(engine) as session:
            user = session.get(User, username)
        return user
    except Exception as e:
        print(f"Error reading user with id={username}: {e}")


# ===================== Problems ======================

def read_all_problems() -> list[Problem]:
    with Session(engine) as session:
        probs = session.query(Problem).all()
    return probs


def read_problem(id: str) -> Problem|None:
    try:
        with Session(engine) as session:
            problem = session.get(Problem, id)
        return problem
    except Exception as e:
        print(f"Error reading problem with id={id}: {e}")


def read_problems_lang(lang: str) -> list[Problem]:
    with Session(engine) as session:
        problems = session.query(Problem).filter(Problem.lang == lang)
    return problems


def add_problem(problem: Problem) -> Problem|None:
    problem.id = str(uuid.uuid4())
    problem.timestamp = dt.datetime.now()
    try:
        with Session(engine) as session:
            session.add(problem)
            session.commit()
            session.refresh(problem) 
        return problem
    except SQLAlchemyError as e:
        logging.error(f"Error adding problem '{problem.title}': {e}")
        return None
  

def edit_problem(problem: Problem) -> Problem|None:
    problem.timestamp = dt.datetime.now()
    try:
        with Session(engine) as session:
            problem_to_edit = session.get(Problem, problem.id)

            # copy problem to problem_to_edit
            mapper = inspect(problem.__class__)
            for column in mapper.columns:
                if column.primary_key:
                    continue
                value = getattr(problem, column.key)
                setattr(problem_to_edit, column.key, value)

            session.commit()
            session.refresh(problem_to_edit) 
            return problem_to_edit
    except Exception as e:
        logging.error(f"Error editing problem with id={problem.id}: {e}")
        return None
    

def delete_problem(id: str) -> Problem|None:
    try:
        with Session(engine) as session:
            problem = session.get(Problem, id)
            if not problem:
                logging.warning(f"Problem with id={id} not found.")
                return None
            session.delete(problem)
            session.commit()
            return problem

    except SQLAlchemyError as e:
        logging.error(f"Error deleting problem with id={id}: {e}")
        return None
