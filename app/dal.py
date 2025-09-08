import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models.pss_models import Ticket

# Створюємо engine (SQLite файл лежить у /data/PSS.db)
engine = create_engine(
    "sqlite:////data/PSS.db",
    echo=True,
    connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency для FastAPI
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def writedown_to_ticket(username, problem_id, solving="", check_message=""):
    db: Session = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.username == username and Ticket.problem_id == problem_id).first()
    now = dt.datetime.now() 
    if (ticket is None):
        # new ticket
        db.add(Ticket(username=username, problem_id=problem_id, when=now, 
                      solving=f"------{now}\n", 
                      check_message=f"------{now}\n"))
    else:
        # existing ticket
        ticket.solving += f"------{now}\n{solving}\n"
        ticket.check_message += f"------{now}\n{check_message}\n" 

    db.commit()
   

