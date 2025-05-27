from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.groupe import Groupe
from app.schemas.groupe import GroupeCreate, GroupeOut
from app.auth import get_current_user  # <--- importe le gestionnaire JWT
from app.models.utilisateur_groupe import UtilisateurGroupe
from typing import List



router = APIRouter(
    prefix="/groupes",
    tags=["groupes"]
)

@router.post("/", response_model=GroupeOut)
def create_groupe(
    groupe: GroupeCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    # Création du groupe
    db_groupe = Groupe(nom=groupe.nom, description=groupe.description)
    db.add(db_groupe)
    db.commit()
    db.refresh(db_groupe)

    # Ajout automatique du créateur dans utilisateur_groupe
    membre = UtilisateurGroupe(
        utilisateur_id=user.id,  # extrait depuis le JWT
        groupe_id=db_groupe.id,
        role="Créateur"  # ou "Admin"
    )
    db.add(membre)
    db.commit()

    return db_groupe
@router.get("/", response_model=List[GroupeOut])
def get_user_groupes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    groupes = (
        db.query(Groupe)
        .join(UtilisateurGroupe)
        .filter(UtilisateurGroupe.utilisateur_id == user.id)
        .all()
    )
    return groupes