import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

import settings.models  # noqa: F401 — regista modelos antes de create_all
from settings.models import Base

load_dotenv()


# ---------------------------------------------------------------------------
# Base de dados Oracle
# ---------------------------------------------------------------------------

DATABASE_URL = URL.create(
    drivername="oracle+oracledb",
    username=os.getenv("ORACLE_USER"),
    password=os.getenv("ORACLE_PASSWORD"),
    host=os.getenv("ORACLE_HOST", "localhost"),
    port=int(os.getenv("ORACLE_PORT", "1521")),
    query={
        "service_name": os.getenv("ORACLE_SERVICE", "FREEPDB1"),
    },
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Aplicação FastAPI
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    yield

    engine.dispose()


app = FastAPI(
    title="RiskPilot GRC Platform",
    version="0.1.0",
    lifespan=lifespan,
)

from settings.routes import api_router as settings_router  # noqa: E402

app.include_router(settings_router, prefix="/api/v1")
