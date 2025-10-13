import os
from collections.abc import AsyncGenerator
from dotenv import load_dotenv

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

from app.models.base import Base
from app.models.users import User
from app.models.extraction_job import ExtractionJob
from app.models.users_consumption import UserUsage
from app.utils.logs import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    try:
        logger.info("Starting database table creation...")
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during table creation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during table creation: {e}")
        raise


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)