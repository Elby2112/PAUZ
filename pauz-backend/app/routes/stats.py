from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from app.dependencies import get_current_user
from app.database import get_session
from app.models import User, GuidedJournal, FreeJournal
from app.services.guided_journal_service import guided_journal_service

router = APIRouter()

@router.get("/guided_journals/total")
def get_total_guided_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of guided journals for the current user from SmartBucket.
    """
    try:
        # Get guided journals from updated guided_journal_service
        guided_journals = guided_journal_service.get_user_guided_journals(current_user.id)
        total_guided_journals = len(guided_journals)
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
    Retrieves the total count of all journals (guided and free) for the current user.
    """
    # Get guided journals from updated guided_journal_service
    try:
        guided_journals = guided_journal_service.get_user_guided_journals(current_user.id)
        total_guided_journals = len(guided_journals)
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
    Retrieves all user statistics in one call for the profile overview.
    """
    # Get guided journals from updated guided_journal_service (KEY FIX!)
    try:
        print(f"🔍 Getting guided journals for user: {current_user.id}")
        guided_journals = guided_journal_service.get_user_guided_journals(current_user.id)
        total_guided_journals = len(guided_journals)
        print(f"✅ Found {total_guided_journals} guided journals in SmartBucket for {current_user.email}")
    except Exception as e:
        print(f"❌ Error getting guided journals from SmartBucket: {e}")
        # Fallback to database count
        total_guided_journals = db.scalar(
            select(func.count()).where(GuidedJournal.user_id == current_user.id)
        ) or 0
        print(f"📊 Fallback: {total_guided_journals} guided journals from database")
    
    # Get free journals from database
    total_free_journals = db.scalar(
        select(func.count()).where(FreeJournal.user_id == current_user.id)
    ) or 0
    
    # Get garden count with error handling
    total_flowers = 0
    try:
        from app.models import Garden
        total_flowers = db.scalar(
            select(func.count()).where(Garden.user_id == current_user.id)
        ) or 0
    except Exception as e:
        print(f"Error getting garden count: {e}")
        total_flowers = 0
    
    total_journals = total_guided_journals + total_free_journals
    
    print(f"📊 Final stats for {current_user.email}:")
    print(f"   - Guided Journals: {total_guided_journals}")
    print(f"   - Free Journals: {total_free_journals}")
    print(f"   - Total Journals: {total_journals}")
    print(f"   - Garden Flowers: {total_flowers}")
    
    return {
        "total_journals": total_journals,
        "total_free_journals": total_free_journals,
        "total_guided_journals": total_guided_journals,
        "total_flowers": total_flowers,
        "user_info": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "picture": current_user.picture
        }
    }