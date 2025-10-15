import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.extractor import router as extractor_router, limiter
from app.routes.auth import router as auth_router
from app.routes.api import router as api_router
from app.database import create_db_and_tables, get_async_session
from app.utils.logs import logger
import uvicorn


load_dotenv()

# Validate required environment variables
def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
    }
    
    # Make GOOGLE_API_KEY optional for now to allow startup
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.warning("⚠️ GOOGLE_API_KEY is not set - LLM extraction features will not work")
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        logger.error("Please set these environment variables before starting the application")
        raise RuntimeError(error_msg)
    
    logger.info("✅ Essential environment variables are set")
    if google_api_key:
        logger.info("✅ GOOGLE_API_KEY is set")
    
    return True

# Validate environment early
validate_environment()

FRONTEND_URL = os.getenv("FRONTEND_URL")
APP_ENV = os.getenv("APP_ENV", "dev")

# Define allowed origins - Configuration CORS plus permissive pour debug
origins = [
    "https://speedx-eta.vercel.app",  # Production frontend
    "https://speedx-backend-v1ol.onrender.com",  # Production backend
    "http://localhost:3000",          # Local development
    "http://127.0.0.1:3000",         # Local development alternative
    "http://localhost:8000",          # Local backend
    "http://127.0.0.1:8000",         # Local backend alternative
    "*"  # Temporairement permissif pour debug
]

# Add FRONTEND_URL if it's set and not already in the list
if FRONTEND_URL and FRONTEND_URL not in origins:
    origins.append(FRONTEND_URL)

# Add any additional CORS origins from environment variable
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
for origin in CORS_ORIGINS:
    origin = origin.strip()
    if origin and origin not in origins:
        origins.append(origin)

# Log the allowed origins for debugging
logger.info(f"CORS allowed origins: {origins}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("=== DÉMARRAGE DE L'APPLICATION SPEEDX ===")
        await create_db_and_tables()
        logger.info("=== APPLICATION DÉMARRÉE AVEC SUCCÈS ===")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {e}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Re-raise l'erreur pour que l'application ne démarre pas en cas de problème
        raise
    
    yield
    
    logger.info("=== APPLICATION FERMÉE ===")

app = FastAPI(
    title="SpeedX API - Extracteur de Relevés Bancaires",
    description="API pour l'extraction automatique de données à partir de relevés bancaires PDF",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if APP_ENV == "dev" else None,
    redoc_url="/redoc" if APP_ENV == "dev" else None
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

app.include_router(auth_router, prefix="/api")
app.include_router(extractor_router, prefix="/api")
app.include_router(api_router, prefix='/api')


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return await http_exception_handler(request, exc)


@app.get("/")
async def root():
    """Simple root endpoint to verify the application is running"""
    return {
        "message": "SpeedX API is running",
        "status": "healthy",
        "version": "1.0.0",
        "environment": APP_ENV
    }

@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(select(1))
    except Exception:
        raise HTTPException(503, "Database unreachable")
    return {"status": "healthy"}

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check that doesn't require database access"""
    return {
        "status": "healthy",
        "message": "Application is running",
        "timestamp": "2025-10-15T00:53:39Z"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render définit $PORT automatiquement
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)

