import re
from datetime import datetime, timedelta
from typing import List, TypedDict
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String)
    attr: Mapped[str] = mapped_column(String)
    lang: Mapped[str] = mapped_column(String)  # py, cs, js, hs
    cond: Mapped[str] = mapped_column(String)
    view: Mapped[str] = mapped_column(String)
    hint: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String)  
    timestamp: Mapped[str] = mapped_column(DateTime)
    # nav
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="problem", cascade="all, delete-orphan")

    @property
    def inline(self):  
        """
cs/002/60/Ряд Сінуса........................aab65ae1-376b-4f52-b120-5513457dd43f (id = inline[44:80])

       using in templates/problemset/edit.html 
        """
        s = (self.attr + "/" + self.title)[:40]
        s += " " * (44 - len(s)) + str(self.id)
        return s
    

class ProblemSet(Base):
    """
    format of problem_ids field  (id=line[44:80])
    "attr/title          -54-2werif-03t34-fgwegvk340-g"   
    "attr/title          -54-2werif-03t34-fgwegvk340-g"
    ...
    """
    __tablename__ = "problemsets"

    id: Mapped[str] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String)
    problem_ids: Mapped[str] = mapped_column(Text)
    open_time: Mapped[datetime] = mapped_column(DateTime)
    open_minutes: Mapped[int] = mapped_column(Integer, default=0)
    stud_filter: Mapped[str] = mapped_column(String, default='')

# --------------- problem_ids methods

        # [44:80] - problem id live here !!!!!
  
    def get_problem_ids_list(self) -> List[str]:
        """return list of problem ids"""
        if not self.problem_ids:
            return []
        return [line[44:80] for line in self.problem_ids.splitlines()]

    def set_problem_ids(self, lst: List[str] ):
        self.problem_ids = "\n".join(lst)
    
    def get_prob_id_by_name(self, name:str):
        res = [line[44:80] for line in self.problem_ids.splitlines() if name in line ]
        return res[0] if len(res) == 1 else None
    
    def get_prob_comment_by_id(self, problem_id:str):
        res = [line[80:].strip() for line in self.problem_ids.splitlines() if problem_id in line ]
        return res[0] if len(res) == 1 else None


# --------------- time props

    @property
    def close_time(self) -> datetime: 
        return self.open_time + timedelta(minutes=self.open_minutes)

    @property
    def rest_time(self) -> timedelta:
        """Return remaining open time, or zero if already closed."""
        if self.open_minutes == 0:
            return timedelta.max
        remaining = self.open_time - datetime.now() + timedelta(minutes=self.open_minutes)
        return max(remaining, timedelta(0))

    @property
    def is_open(self) -> bool: 
        return self.open_time < datetime.now() < self.close_time;



class Ticket(Base):

    class TicketRecord(TypedDict):
        when: str
        code: str
        check: str

    __tablename__ = "tickets"
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String)
    problem_id: Mapped[str] = mapped_column(String, ForeignKey("problems.id", ondelete="CASCADE")) 
    records: Mapped[str] = mapped_column(Text, default="")
    track: Mapped[str] = mapped_column(Text, default="")
    expire_time: Mapped[datetime] = mapped_column(DateTime)
    state: Mapped[int] = mapped_column(Integer, default=0) # 1 - problem is solved
    #  nav
    problem: Mapped["Problem"] = relationship(back_populates="tickets")

# --------------- record methods

    def add_record(self, solving, check_message):  
        RECORD_FORMAT = "~0~{0}\n~1~{1}\n~2~{2:%Y-%m-%d %H:%M:%S}\n~3~\n"
        self.records += RECORD_FORMAT.format(solving, check_message, datetime.now())
        if check_message.startswith("OK") and self.state == 0:
            self.state = 1
    
    def get_records(self) -> List[TicketRecord]:
        """ 
        Отримання записів у вигляді списку словників TicketRecord.
        """
        REGEX = r"~0~(.*?)~1~(.*?)~2~(.*?)~3~"
        matches = re.findall(REGEX, self.records, flags=re.S)
        return [{"when": m[2], "code":m[0].strip(), "check":m[1].strip()} for m in matches]

    def when_success(self) -> datetime:
        records = self.get_records()
        success_records = [r for r in records if r["check"].startswith("OK") ]
        if len(success_records) == 0:
            return datetime.min
        when = success_records[0]["when"].strip()
        return datetime.fromisoformat(when)
    
    def solving_duration(self) -> timedelta:
        """
        Час, витрачений на успішне вирішення.
        """
        if self.state != 1:
            return timedelta(0)
        records = self.get_records()
        when = records[0]["when"].strip()
        t_start = datetime.fromisoformat(when) 
        success_records = [r for r in records if r["check"].startswith("OK") ]
        when = success_records[0]["when"].strip()
        t_stop = datetime.fromisoformat(when)
        return t_stop - t_start
    

    SECONDHAND = "SECONDHAND"

    def is_secondhand(self):
        """ Маркер, чи відкоивалася задача повторно. """
        records = self.get_records()
        return len(records) > 1 and records[1]["check"] == Ticket.SECONDHAND



class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[str] = mapped_column(String)     # 'student', 'tutor', 'admin'

   