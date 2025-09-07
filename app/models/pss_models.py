""" All models for PSS.db """
import datetime as dt
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


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
    #
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="problem", cascade="all, delete-orphan")


class User(Base):
    """
    role: student, tutor, admin
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[str] = mapped_column(String)
    #
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user", cascade="all, delete-orphan")

# =============================================================

class ProblemSet(Base):
    __tablename__ = "problemsets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    problem_ids: Mapped[str] = mapped_column(Text)
    open_time: Mapped[dt.datetime] = mapped_column(DateTime)
    open_minutes: Mapped[int] = mapped_column(Integer)

    def is_open(this) -> bool:
        if this.open_time is None or this.open_minutes is None:
            return False
        limit: dt.datetime = this.open_time + dt.timedelta(minutes=this.open_minutes)
        return limit > dt.datetime.now()


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, ForeignKey("users.username", ondelete="CASCADE"))
    problem_id: Mapped[str] = mapped_column(String, ForeignKey("problems.id", ondelete="CASCADE")) 
    when: Mapped[dt.datetime] = mapped_column(DateTime)
    solving: Mapped[str] = mapped_column(Text)
    check_message: Mapped[str] = mapped_column(String)   
    # 
    user: Mapped["User"] = relationship(back_populates="tickets")
    problem: Mapped["Problem"] = relationship(back_populates="tickets")
   

