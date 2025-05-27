from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.auth import get_current_user
from app.models.user import Utilisateur
from app.services.planning_auto import generer_planning_pour_utilisateur  # ta fonction algorithme

router = APIRouter(prefix="/planning", tags=["planning"])

@router.post("/generer")
def generer_planning(db: Session = Depends(get_db), user: Utilisateur = Depends(get_current_user)):
    try:
        planning = generer_planning_pour_utilisateur(db, user.id)
        return {"message": "Planning généré avec succès", "planning_id": planning.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
