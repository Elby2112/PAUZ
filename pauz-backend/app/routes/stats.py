from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.dependencies import get_current_user
from app.database import get_session
from app.models.user import User
from app.models.guided_journal import GuidedJournal
from app.models.free_journal import FreeJournal

router = APIRouter()

@router.get("/guided_journals/total")
def get_total_guided_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of guided journals for the current user.
    """
    total_guided_journals = db.exec(
        select(GuidedJournal).where(GuidedJournal.user_id == current_user.id)
    ).count()
    return {"total_guided_journals": total_guided_journals}

@router.get("/free_journals/total")
def get_total_free_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of free journals for the current user.
    """
    total_free_journals = db.exec(
        select(FreeJournal).where(FreeJournal.user_id == current_user.id)
    ).count()
    return {"total_free_journals": total_free_journals}

@router.get("/journals/total")
def get_total_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves the total count of all journals (guided and free) for the current user.
    """
    total_guided_journals = db.exec(
        select(GuidedJournal).where(GuidedJournal.user_id == current_user.id)
    ).count()
    total_free_journals = db.exec(
        select(FreeJournal).where(FreeJournal.user_id == current_user.id)
    ).count()
    total_journals = total_guided_journals + total_free_journals
    return {"total_journals": total_journals}
