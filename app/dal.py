from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

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



# engine = create_engine(f"sqlite:////data/PSS.db", echo=True)

# def get_db():
#     return Session(engine)


   

