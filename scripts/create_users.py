import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.users import User, UserRole
from app.core.security import get_password_hash
import uuid


# Configuration de la base de données
DATABASE_URL = "sqlite+aiosqlite:///./speedx.db"  # Modifiez selon votre config


async def create_users():
    """Crée un utilisateur standard et un utilisateur admin"""
    
    # Créer le moteur de base de données
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Utilisateur ADMIN
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
            
            # Utilisateur STANDARD
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
            
            # Ajouter les utilisateurs à la session
            session.add(admin_user)
            session.add(standard_user)
            
            # Commit les changements
            await session.commit()
            
            print("✅ Utilisateurs créés avec succès !")
            print("\n📧 Utilisateur ADMIN:")
            print(f"   Email: admin@speedx.com")
            print(f"   Mot de passe: Admin123!")
            print(f"   ID: {admin_user.id}")
            
            print("\n📧 Utilisateur STANDARD:")
            print(f"   Email: user@speedx.com")
            print(f"   Mot de passe: User123!")
            print(f"   ID: {standard_user.id}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des utilisateurs: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("🚀 SpeedX - Création d'utilisateurs\n")
    asyncio.run(create_users())