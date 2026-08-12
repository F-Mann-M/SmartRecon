from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from contextlib import contextmanager

from core.config import settings


engine = create_engine(settings.DATABASE_URL) # , echo=True
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

def get_db_fastapi():
    """Generator for FastAPI routes. Managed automatically by Depends()."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. For Standalone Scripts / Background Tasks (Context Manager)
@contextmanager
def get_db():
    """Context manager for scripts, CLI commands, and worker jobs."""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Auto-commit on clean exit
    except Exception:
        db.rollback()  # Auto-rollback on error
        raise
    finally:
        db.close()