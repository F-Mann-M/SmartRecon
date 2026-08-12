from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager

from core.config import settings


engine = create_engine(settings.DATABASE_URL) # , echo=True
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

@contextmanager
def get_db():
    """Provides a transactional database session for FastAPI or scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def get_db_session():
#     """Return a normal SQLAlchemy Session for non-dependency-injection use cases."""
#     return SessionLocal()
