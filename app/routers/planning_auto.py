from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.planning_auto import generer_planning_pour_utilisateur

router = APIRouter(prefix="/planning-auto", tags=["Planning Auto"])

@router.post("/{utilisateur_id}")
def lancer_generation_planning(utilisateur_id: int, db: Session = Depends(get_db)):
    generer_planning_pour_utilisateur(utilisateur_id, db)
    return {"message": "Planning généré automatiquement"}
