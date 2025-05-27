from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.tache_planifiee import TachePlanifieeCreate, TachePlanifieeUpdate
from app.models.tache_planifiee import TachePlanifiee
from app.database.db import get_db
from app.auth import get_current_user
from app.models.planning import Planning  # Associer des tâches à un planning
from app.models.tache import Tache  # Si tu veux associer des tâches à des tâches planifiées
from datetime import datetime, timedelta
from fastapi import Query
from sqlalchemy.orm import joinedload




router = APIRouter()

# Route pour créer une tâche planifiée
@router.post("/taches_planifiees/")
def create_tache_planifiee(tache_planifiee: TachePlanifieeCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    # Vérifie si le planning existe pour l'utilisateur
    planning = db.query(Planning).filter(Planning.id == tache_planifiee.planning_id, Planning.utilisateur_id == user.id).first()
    if not planning:
        raise HTTPException(status_code=404, detail="Planning non trouvé")

    # Créer la tâche planifiée avec la date de début et de fin
    db_tache_planifiee = TachePlanifiee(
        tache_id=tache_planifiee.tache_id,
        planning_id=tache_planifiee.planning_id,
        date_debut=tache_planifiee.date_debut,   # Utilisation de la date de début
        date_fin=tache_planifiee.date_fin,       # Utilisation de la date de fin
        duree=tache_planifiee.duree              # Utilisation de la durée
    )
    db.add(db_tache_planifiee)
    db.commit()
    db.refresh(db_tache_planifiee)
    return db_tache_planifiee

# Route pour obtenir toutes les tâches planifiées d'un utilisateur
@router.get("/taches_planifiees/")
def get_all_taches_planifiees(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """
    Récupère toutes les tâches planifiées associées à l'utilisateur connecté.
    """
    return db.query(TachePlanifiee).join(Planning).filter(Planning.utilisateur_id == user.id).all()

# Route pour obtenir une tâche planifiée spécifique
@router.get("/taches_planifiees/{tache_planifiee_id}")
def get_tache_planifiee(tache_planifiee_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """
    Récupère une tâche planifiée spécifique associée à l'utilisateur connecté.
    """
    tache_planifiee = db.query(TachePlanifiee).join(Planning).filter(
        TachePlanifiee.id == tache_planifiee_id, Planning.utilisateur_id == user.id
    ).first()
    if not tache_planifiee:
        raise HTTPException(status_code=404, detail="Tâche planifiée non trouvée")
    return tache_planifiee

# Route pour mettre à jour une tâche planifiée
@router.put("/taches_planifiees/{tache_planifiee_id}")
def update_tache_planifiee(tache_planifiee_id: int, updates: TachePlanifieeUpdate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """
    Met à jour une tâche planifiée spécifique si elle appartient à l'utilisateur connecté.
    """
    tache_planifiee = db.query(TachePlanifiee).join(Planning).filter(
        TachePlanifiee.id == tache_planifiee_id, Planning.utilisateur_id == user.id
    ).first()
    if not tache_planifiee:
        raise HTTPException(status_code=404, detail="Tâche planifiée non trouvée")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(tache_planifiee, key, value)
    db.commit()
    return tache_planifiee

# Route pour supprimer une tâche planifiée
@router.delete("/taches_planifiees/{tache_planifiee_id}")
def delete_tache_planifiee(tache_planifiee_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """
    Supprime une tâche planifiée spécifique si elle appartient à l'utilisateur connecté.
    """
    tache_planifiee = db.query(TachePlanifiee).join(Planning).filter(
        TachePlanifiee.id == tache_planifiee_id, Planning.utilisateur_id == user.id
    ).first()
    if not tache_planifiee:
        raise HTTPException(status_code=404, detail="Tâche planifiée non trouvée")

    db.delete(tache_planifiee)
    db.commit()
    return {"message": "Tâche planifiée supprimée avec succès"}
#tache planifier pour un jour 
@router.get("/taches_planifiees/jour/")
def get_taches_planifiees_par_jour(
    date: datetime = Query(..., description="Date (YYYY-MM-DD) pour filtrer"),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    date_debut = date.replace(hour=0, minute=0, second=0, microsecond=0)
    date_fin = date_debut + timedelta(days=1)

    # Chargement "join" pour récupérer la tâche liée en même temps
    taches_jour = db.query(TachePlanifiee).join(Planning).filter(
        Planning.utilisateur_id == user.id,
        TachePlanifiee.date_debut >= date_debut,
        TachePlanifiee.date_debut < date_fin
    ).options(joinedload(TachePlanifiee.tache)).all()

    # On peut retourner directement les objets, FastAPI va les sérialiser si tu as les bons schemas Pydantic
    # Sinon, on peut construire une liste personnalisée :
    result = []
    for tp in taches_jour:
        result.append({
            "id": tp.id,
            "date_debut": tp.date_debut,
            "duree": tp.duree,
            "titre_tache": tp.tache.titre,
            "description_tache": tp.tache.description,
            # ajoute d’autres champs si besoin
        })

    return result
