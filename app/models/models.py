""" All models for PSS.db """
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Problem(Base):
    __tablename__ = "problems"
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    attr: Mapped[str] = mapped_column(String)
    lang: Mapped[str] = mapped_column(String)
    cond: Mapped[str] = mapped_column(String)
    view: Mapped[str] = mapped_column(String)
    hint: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String)  
    timestamp: Mapped[str] = mapped_column(DateTime)


class User(Base):
    """ password hashed
    """
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[str] = mapped_column(String)

# =============================================================

class ProblemSet(Base):
    __tablename__ = "problemsets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    problem_ids: Mapped[str] = mapped_column(Text)
    open_time: Mapped[datetime] = mapped_column(DateTime)
    open_minutes: Mapped[int] = mapped_column(Integer)


class Ticket(Base):
    __tablename__ = "tickets"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    problem_id: Mapped[str] = mapped_column(String, primary_key=True)    
    last_change_time: Mapped[datetime] = mapped_column(DateTime)
    solving: Mapped[str] = mapped_column(Text)
    check_message: Mapped[str] = mapped_column(String)



