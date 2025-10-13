from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.models.users import User
from app.models.extraction_job import ExtractionJob, JobStatus
from app.services.auth.auth import current_active_user, get_admin_user
from app.database import get_async_session

router = APIRouter(tags=["api"])


@router.get("/user/profile")
async def get_user_profile(user: User = Depends(current_active_user)):
    """Récupère le profil de l'utilisateur connecté."""
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Récupère les statistiques pour le tableau de bord de l'utilisateur connecté."""
    
    # Get extraction job statistics for the current user
    result = await session.execute(
        select(
            func.count(ExtractionJob.id).label("total_extractions"),
            func.sum(case((ExtractionJob.status == JobStatus.success, 1), else_=0)).label("successful_extractions"),
            func.sum(case((ExtractionJob.status == JobStatus.failed, 1), else_=0)).label("failed_extractions"),
        ).where(ExtractionJob.user_id == user.id)
    )
    
    stats = result.first()
    total = stats.total_extractions or 0
    successful = stats.successful_extractions or 0
    failed = stats.failed_extractions or 0
    
    # Calculate success rate
    success_rate = (successful / total * 100) if total > 0 else 0
    
    # Get recent files (last 5 extraction jobs)
    recent_files_result = await session.execute(
        select(ExtractionJob.pdf_filename, ExtractionJob.status, ExtractionJob.submitted_at)
        .where(ExtractionJob.user_id == user.id)
        .order_by(ExtractionJob.submitted_at.desc())
        .limit(5)
    )
    
    recent_files = [
        {
            "filename": row.pdf_filename,
            "status": row.status.value,
            "submitted_at": row.submitted_at.isoformat()
        }
        for row in recent_files_result.fetchall()
    ]
    
    return {
        "total_extractions": total,
        "successful_extractions": successful,
        "failed_extractions": failed,
        "success_rate": round(success_rate, 2),
        "recent_files": recent_files
    }

@router.get("/admin/dashboard")
async def get_admin_dashboard(
    admin_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Récupère les données du tableau de bord administrateur."""
    
    # Get total users count
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Get active users count (users who have submitted at least one job)
    active_users_result = await session.execute(
        select(func.count(func.distinct(ExtractionJob.user_id)))
    )
    active_users = active_users_result.scalar() or 0
    
    # Get total extractions across all users
    total_extractions_result = await session.execute(
        select(func.count(ExtractionJob.id))
    )
    total_extractions = total_extractions_result.scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_extractions": total_extractions,
        "system_health": "good"
    }


@router.get("/admin/users/stats")
async def get_users_stats(
    admin_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Récupère les statistiques détaillées de tous les utilisateurs pour l'admin."""
    
    # Get statistics for each user
    result = await session.execute(
        select(
            User.id,
            User.email,
            User.is_active,
            func.count(ExtractionJob.id).label("total_extractions"),
            func.sum(case((ExtractionJob.status == JobStatus.success, 1), else_=0)).label("successful_extractions"),
            func.sum(case((ExtractionJob.status == JobStatus.failed, 1), else_=0)).label("failed_extractions"),
            func.max(ExtractionJob.submitted_at).label("last_activity")
        )
        .outerjoin(ExtractionJob, User.id == ExtractionJob.user_id)
        .group_by(User.id, User.email, User.is_active)
        .order_by(User.email)
    )
    
    users_stats = []
    for row in result.fetchall():
        total = row.total_extractions or 0
        successful = row.successful_extractions or 0
        failed = row.failed_extractions or 0
        success_rate = (successful / total * 100) if total > 0 else 0
        
        users_stats.append({
            "user_id": str(row.id),
            "email": row.email,
            "is_active": row.is_active,
            "total_extractions": total,
            "successful_extractions": successful,
            "failed_extractions": failed,
            "success_rate": round(success_rate, 2),
            "last_activity": row.last_activity.isoformat() if row.last_activity else None
        })
    
    return {
        "users": users_stats,
        "total_users": len(users_stats)
    }
