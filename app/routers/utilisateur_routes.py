from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.models.user import Utilisateur
from app.schemas.user import UtilisateurRead

router = APIRouter(
    prefix="/utilisateurs",
    tags=["utilisateurs"]
)

@router.get("/", response_model=List[UtilisateurRead])
def get_all_utilisateurs(db: Session = Depends(get_db)):
    utilisateurs = db.query(Utilisateur).all()
    return utilisateurs
