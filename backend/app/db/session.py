import ssl
from typing import AsyncGenerator
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings


# Base engine configuration
if settings.ENVIRONMENT == "cloud":
    from azure.identity.aio import DefaultAzureCredential

    # For User-Assigned Managed Identity, pass client_id if configured
    credential = (
        DefaultAzureCredential(managed_identity_client_id=settings.AZURE_CLIENT_ID)
        if settings.AZURE_CLIENT_ID
        else DefaultAzureCredential()
    )

    # Cloud connection URL (no static password provided)
    # Format: postgresql+asyncpg://<managed_identity_username>@<host>:<port>/<dbname>
    DATABASE_URL = settings.DATABASE_URL  

    # Require SSL for Azure Database for PostgreSQL Flexible Server
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async def get_token_password():
        """Fetches fresh ephemeral token from IMDS for each new physical connection."""
        token = await credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
        return token.token

    engine = create_async_engine(
        DATABASE_URL,
        connect_args={
            "ssl": ssl_context,
            "password": get_token_password,  # asyncpg supports async callable for password
        },
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,  # Recycle connections before 1hr Azure token expiry
    )

else:
    # Local connection URL (standard user/password)
    # Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
    DATABASE_URL = settings.DATABASE_URL

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Useful for debugging SQL in local development
        pool_pre_ping=True,
    )

# Session factory (identical for both local and cloud)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency injection for FastAPI routes
async def get_db_fastapi() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for route handlers via Depends(get_db_fastapi)."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()



# For Background Tasks, Celery/ARQ workers, Cron jobs, CLI Scripts
@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for background workers: async with get_db() as session:"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()




# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
# from contextlib import contextmanager

# from core.config import settings


# engine = create_engine(settings.DATABASE_URL) # , echo=True
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# class Base(DeclarativeBase):
#     pass

# def get_db_fastapi():
#     """Generator for FastAPI routes. Managed automatically by Depends()."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # For Standalone Scripts / Background Tasks (Context Manager)
# @contextmanager
# def get_db():
#     """Context manager for scripts, CLI commands, and worker jobs."""
#     db = SessionLocal()
#     try:
#         yield db
#         db.commit()  # Auto-commit on clean exit
#     except Exception:
#         db.rollback()  # Auto-rollback on error
#         raise
#     finally:
#         db.close()
        
    