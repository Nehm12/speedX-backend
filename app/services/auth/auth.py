import os
import uuid
from dotenv import load_dotenv
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, CookieTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from app.models.users import User, UserRole
from app.database import get_user_db
from app.utils.logs import logger
from app.services.email.email_service import email_service

load_dotenv()

SECRET = os.getenv("SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
LIFETIME_SECONDS = 3600 * 24 * 30

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(
    cookie_max_age=LIFETIME_SECONDS, 
    cookie_name="session",
    cookie_secure=True,
    cookie_samesite="none",
    cookie_httponly=True
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.email} has been registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        
        # Essayer d'envoyer l'email
        email_sent = await email_service.send_password_reset_email(user.email, token)
        
        if email_sent:
            logger.info(f"Email de réinitialisation envoyé avec succès à {user.email}")
        else:
            # Mode développement: afficher le lien dans les logs
            reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
            logger.info(f"🔗 LIEN DE RÉINITIALISATION (DEV MODE): {reset_url}")
            logger.warning("⚠️  Mode développement: Copiez le lien ci-dessus pour tester la réinitialisation.")
            
            # En développement, considérer comme succès pour permettre les tests
            if not email_service.is_configured():
                logger.info("Mode développement activé - pas d'envoi d'email réel")
            else:
                logger.error("Échec de l'envoi d'email malgré la configuration")
                # Ne pas lever d'exception pour éviter l'erreur côté frontend
                # L'utilisateur recevra tout de même le token via les logs en mode dev

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        logger.info(f"Verification token generated for user {user.email}: {token}")
    
    async def is_admin(self, user: User) -> bool:
        return user.role == UserRole.ADMIN or user.is_superuser

"""Manage users authentification using JWT and Cookies Session Manager"""

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=LIFETIME_SECONDS)

jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [jwt_backend, cookie_backend])
current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


async def get_admin_user(
    user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager)
):
    if not await user_manager.is_admin(user):
        raise Exception("Admin privileges required")
    return user