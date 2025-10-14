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
FRONTEND_URL = os.getenv("FRONTEND_URL")
APP_ENV = os.getenv("APP_ENV", "dev")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Clean up any empty strings from split
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    logger.info("Application démarrée avec succès")
    yield
    
    logger.info("Application fermée")

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

# Configuration CORS dynamique selon l'environnement
if APP_ENV == "prod":
    allowed_origins = CORS_ORIGINS.copy()
    # Always include the frontend URL if it's set
    if FRONTEND_URL and FRONTEND_URL not in allowed_origins:
        allowed_origins.append(FRONTEND_URL)
    
    # Log the allowed origins for debugging
    logger.info(f"Production CORS allowed origins: {allowed_origins}")
else:
    # Development environment - allow localhost
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    if FRONTEND_URL and FRONTEND_URL not in allowed_origins:
        allowed_origins.append(FRONTEND_URL)
    
    logger.info(f"Development CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

app.include_router(auth_router, prefix="/api")
app.include_router(extractor_router, prefix="/api")
app.include_router(api_router, prefix='/api')


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return await http_exception_handler(request, exc)


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(select(1))
    except Exception:
        raise HTTPException(503, "Database unreachable")
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render définit $PORT automatiquement
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)

