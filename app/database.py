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

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def seed_default_users():
    """Crée les utilisateurs par défaut s'ils n'existent pas déjà"""
    async with async_session_maker() as session:
        try:
            logger.info("🔍 Vérification des utilisateurs existants...")

            # Vérifier admin
            admin_result = await session.execute(select(User).where(User.email == "admin@speedx.com"))
            existing_admin = admin_result.scalar_one_or_none()

            # Vérifier standard
            user_result = await session.execute(select(User).where(User.email == "user@speedx.com"))
            existing_user = user_result.scalar_one_or_none()

            users_created = []

            if not existing_admin:
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
                logger.info("✅ Utilisateur ADMIN créé")
            else:
                logger.info("ℹ️ Utilisateur ADMIN existe déjà")

            if not existing_user:
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
                logger.info("✅ Utilisateur STANDARD créé")
            else:
                logger.info("ℹ️ Utilisateur STANDARD existe déjà")

            if users_created:
                await session.commit()
                logger.info(f"🎉 Utilisateurs créés avec succès: {', '.join(users_created)}")
            else:
                logger.info("ℹ️ Aucun nouvel utilisateur à créer")

        except Exception as e:
            logger.error(f"❌ Erreur lors du seeding des utilisateurs: {e}")
            await session.rollback()
            raise


async def create_db_and_tables():
    """Crée la base et les tables, puis seed les utilisateurs"""
    try:
        logger.info("🚀 Démarrage de la création des tables de la base...")

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Connexion à la base réussie")

            await conn.run_sync(Base.metadata.create_all)
            logger.info("🎯 Tables créées avec succès")

        # Seed des utilisateurs par défaut
        await seed_default_users()

    except SQLAlchemyError as e:
        logger.error(f"❌ Erreur SQLAlchemy lors de la création des tables: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la création des tables: {e}")
        raise


# Générateurs pour dépendances FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

# Configuration CORS