from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.models.users import User
from app.schemas.users import UserCreate, UserRead, UserUpdate
from app.services.auth.auth import fastapi_users, get_admin_user, current_active_user, jwt_backend, cookie_backend, get_user_manager, UserManager
from app.utils.logs import logger

router = APIRouter(tags=["Authentification"])

"""Add fastapi_users default routes for authentification"""
router.include_router(
    fastapi_users.get_auth_router(jwt_backend), 
    prefix="/auth/jwt"
)
router.include_router(
    fastapi_users.get_auth_router(cookie_backend), 
    prefix="/auth/cookie"
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), 
    prefix="/auth"
)
router.include_router(
    fastapi_users.get_reset_password_router(), 
    prefix="/auth"
)
router.include_router(
    fastapi_users.get_verify_router(UserRead), 
    prefix="/auth"
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), 
    prefix="/users"
)

@router.get("/users/me", response_model=UserRead)
async def get_current_user(user: User = Depends(current_active_user)):
    return user

"""Admin routes only"""

@router.post("/admin/users", response_model=UserRead)
async def admin_create_user(
    user_create: UserCreate,
    admin_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Create a user"""
    try:
        user = await user_manager.create(user_create, safe=True, request=None)
        return user
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'utilisateur par l'admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/admin/users", response_model=List[UserRead])
async def list_users(
    admin_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Liste tous les utilisateurs (admin uniquement)"""
    query = select(User)
    result = await session.execute(query)
    users = result.scalars().all()
    return users


@router.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    admin_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        # Get user to delete
        user_to_delete = await user_manager.get(user_id)
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Raise error for own deletion
        if str(user_to_delete.id) == str(admin_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account",
            )
        
        await user_manager.delete(user_to_delete)
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'utilisateur: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )