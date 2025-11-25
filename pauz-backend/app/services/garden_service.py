import os
from typing import List, Optional
from sqlmodel import Session, select
from app.models.garden import Garden
from app.database import get_session
from fastapi import Depends
from datetime import datetime

class GardenService:
    def __init__(self):
        pass

    def create_garden_entry(self, user_id: str, mood: str, note: Optional[str], flower_type: str, db: Session = Depends(get_session)) -> Garden:
        """
        Creates a new Garden entry and saves it to the database.
        """
        garden_entry = Garden(user_id=user_id, mood=mood, note=note, flower_type=flower_type)
        db.add(garden_entry)
        db.commit()
        db.refresh(garden_entry)
        return garden_entry

    def get_garden_entries(self, user_id: str, db: Session = Depends(get_session)) -> List[Garden]:
        """
        Retrieves garden entries for a user from the database.
        """
        return db.exec(select(Garden).where(Garden.user_id == user_id)).all()

garden_service = GardenService()
