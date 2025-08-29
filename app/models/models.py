from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Задачник (ProblemSet):
#   id - назва    PK
#   user_id  - id викладача
#   problem_ids - список id задач 
#   open_time - момент відкриття
#   open_minutes - термін відкритості в хвилинах  

class ProblemSet(Base):
    __tablename__ = "problemsets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255))
    problem_ids: Mapped[str] = mapped_column(Text)
    open_time: Mapped[datetime] = mapped_column(DateTime)
    open_minutes: Mapped[int] = mapped_column(Integer)

# Ticket  - створ, коли юзер відкриває задачу
#   user_id  - id викладача    PK
#   problem_id - id задачі   PK
#   last_change_time - дата-час отанньої зміни
#   solving - вирішення
#   check_message - повідомлення перевірки

class Ticket(Base):
    __tablename__ = "tickets"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    problem_id: Mapped[str] = mapped_column(String, primary_key=True)    
    last_change_time: Mapped[datetime] = mapped_column(DateTime)
    solving: Mapped[str] = mapped_column(Text)
    check_message: Mapped[str] = mapped_column(String)


# =============================================================
class Problem(Base):
    __tablename__ = "problems"
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    attr: Mapped[str] = mapped_column(String(255))
    lang: Mapped[str] = mapped_column(String(5))
    cond: Mapped[str] = mapped_column(String)
    view: Mapped[str] = mapped_column(String)
    hint: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String(10))  
    timestamp: Mapped[str] = mapped_column(DateTime)


class User(Base):
    """ password hashed
        role (1 student, 2 tutor, 4 admin) 
    """
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[int] = mapped_column(Integer)
