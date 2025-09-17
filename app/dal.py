from datetime import datetime
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

# Dependency для роутерів
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def writedown_to_ticket(username, problem_id, solving="", check_message=""):
    """
    Формат запису: "~0~ answer ~1~ check messsage ~2~ datetime ~3~"
    """
    RECORD = "~0~{0}\n~1~{1}\n~2~{2:%Y-%m-%dT%H:%M:%S}\n~3~\n"
    with SessionLocal() as db:
        ticket = db.query(Ticket).filter(Ticket.username == username and Ticket.problem_id == problem_id).first()
        now = datetime.now()
        record = RECORD.format(solving, check_message, now)
        if (ticket is None):
            # new ticket 
            # TODO: when & check_message are not needed
            ticket = Ticket(username=username, problem_id=problem_id, records=record, comment="") 
            db.add(ticket)
        else:
            # existing ticket
            ticket.records += record
            # one time OK is always OK
            if not ticket.comment.startswith('OK'):
                ticket.comment = check_message
        db.commit()
