import os
from collections.abc import AsyncGenerator
from dotenv import load_dotenv

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.models.base import Base
from app.models.users import User, UserRole
from app.models.extraction_job import ExtractionJob
from app.models.users_consumption import UserUsage
from app.core.security import get_password_hash
from app.utils.logs import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def seed_default_users():
    """Crée les utilisateurs par défaut s'ils n'existent pas déjà"""
    logger.info("=== DÉBUT DU SEEDING DES UTILISATEURS ===")
    
    async with async_session_maker() as session:
        try:
            # Vérifier si l'utilisateur admin existe déjà
            logger.info("Vérification de l'existence de l'utilisateur admin...")
            admin_query = select(User).where(User.email == "admin@speedx.com")
            admin_result = await session.execute(admin_query)
            existing_admin = admin_result.scalar_one_or_none()
            
            # Vérifier si l'utilisateur standard existe déjà
            logger.info("Vérification de l'existence de l'utilisateur standard...")
            user_query = select(User).where(User.email == "user@speedx.com")
            user_result = await session.execute(user_query)
            existing_user = user_result.scalar_one_or_none()
            
            users_created = []
            
            # Créer l'utilisateur admin s'il n'existe pas
            if not existing_admin:
                logger.info("Création de l'utilisateur admin en cours...")
                admin_user = User(
                    id=uuid.uuid4(),
                    email="admin@speedx.com",
                    hashed_password=get_password_hash("Admin123!"),
                    first_name="Admin",
                    last_name="SpeedX",
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_superuser=True,
                    is_verified=True
                )
                session.add(admin_user)
                users_created.append("admin@speedx.com")
                logger.info("✅ Utilisateur admin préparé pour création")
            else:
                logger.info("ℹ️ Utilisateur admin existe déjà")
            
            # Créer l'utilisateur standard s'il n'existe pas
            if not existing_user:
                logger.info("Création de l'utilisateur standard en cours...")
                standard_user = User(
                    id=uuid.uuid4(),
                    email="user@speedx.com",
                    hashed_password=get_password_hash("User123!"),
                    first_name="Utilisateur",
                    last_name="Standard",
                    role=UserRole.STANDARD,
                    is_active=True,
                    is_superuser=False,
                    is_verified=True
                )
                session.add(standard_user)
                users_created.append("user@speedx.com")
                logger.info("✅ Utilisateur standard préparé pour création")
            else:
                logger.info("ℹ️ Utilisateur standard existe déjà")
            
            # Sauvegarder les changements
            if users_created:
                logger.info("Sauvegarde des nouveaux utilisateurs en cours...")
                await session.commit()
                logger.info(f"🎉 Utilisateurs créés avec succès: {', '.join(users_created)}")
            else:
                logger.info("ℹ️ Aucun nouvel utilisateur à créer")
            
            logger.info("=== FIN DU SEEDING DES UTILISATEURS ===")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du seeding des utilisateurs: {e}")
            logger.error(f"Type d'erreur: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            await session.rollback()
            raise


async def create_db_and_tables():
    try:
        logger.info("Starting database table creation...")
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
        # Seeder les utilisateurs par défaut après la création des tables
        await seed_default_users()
            
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