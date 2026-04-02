import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.routes import auth, records, analytics
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import user, record

# Configure basic logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Ensures database tables are initialized before the app accepts requests.
    """
    logger.info("Starting up Personal Finance Tracker...")
    async with engine.begin() as conn:
        # Auto-create tables (Development/Assigment simplicity)
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down Personal Finance Tracker...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    """
    Global catch-all for unhandled exceptions.
    Prevents leaking internal stack traces in production.
    """
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A critical system error occurred.", "code": "INTERNAL_SERVER_ERROR"},
    )

# Routing Table
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(records.router, prefix=f"{settings.API_V1_STR}/records", tags=["Transaction Records"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Performance Analytics"])

from fastapi.responses import JSONResponse, RedirectResponse

# ... (rest of imports)

@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirects the root path to the interactive API documentation."""
    return RedirectResponse(url="/docs")
