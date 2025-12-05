from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from app.dependencies import get_current_user
from app.database import get_session
from app.models import User, GuidedJournal, FreeJournal
from app.services.guided_journal_service import guided_journal_service
from app.services.stats_service import stats_service

router = APIRouter()

@router.get("/guided_journals/total")
def get_total_guided_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of guided journals for the current user (optimized).
    """
    try:
        total_guided_journals = guided_journal_service.get_user_guided_journals_count(current_user.id)
        print(f"✅ Found {total_guided_journals} guided journals for user {current_user.id}")
        return {"total_guided_journals": total_guided_journals}
    except Exception as e:
        print(f"❌ Error getting guided journals: {e}")
        # Fallback to database count
        total_guided_journals = db.scalar(
            select(func.count()).where(GuidedJournal.user_id == current_user.id)
        ) or 0
        return {"total_guided_journals": total_guided_journals}

@router.get("/free_journals/total")
def get_total_free_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of free journals for the current user.
    """
    total_free_journals = db.scalar(
        select(func.count()).where(FreeJournal.user_id == current_user.id)
    )
    return {"total_free_journals": total_free_journals or 0}

@router.get("/journals/total")
def get_total_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of all journals (guided and free) for the current user (optimized).
    """
    try:
        # Use optimized count for guided journals
        total_guided_journals = guided_journal_service.get_user_guided_journals_count(current_user.id)
        print(f"✅ Found {total_guided_journals} guided journals for total count")
    except Exception as e:
        print(f"❌ Error getting guided journals for total count: {e}")
        total_guided_journals = db.scalar(
            select(func.count()).where(GuidedJournal.user_id == current_user.id)
        ) or 0
    
    # Get free journals from database
    total_free_journals = db.scalar(
        select(func.count()).where(FreeJournal.user_id == current_user.id)
    ) or 0
    
    total_journals = total_guided_journals + total_free_journals
    return {"total_journals": total_journals}

@router.get("/garden/total")
def get_total_garden_flowers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of garden flowers for the current user.
    """
    # Import Garden locally to avoid import issues
    try:
        from app.models import Garden
        total_flowers = db.scalar(
            select(func.count()).where(Garden.user_id == current_user.id)
        )
        return {"total_flowers": total_flowers or 0}
    except ImportError as e:
        print(f"Garden model import error: {e}")
        return {"total_flowers": 0}
    except Exception as e:
        print(f"Database error in garden count: {e}")
        return {"total_flowers": 0}

@router.get("/overview")
def get_user_overview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves all user statistics in one call for the profile overview (optimized with caching).
    """
    # Use the optimized stats service with caching
    stats = stats_service.get_user_stats_optimized(current_user.id, db)
    
    # Add user info
    stats["user_info"] = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "picture": current_user.picture
    }
    
    return stats