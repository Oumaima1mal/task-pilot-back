from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.tache import TacheCreate, TacheUpdate, TacheStatutUpdate
from app.models.tache import Tache
from app.database.db import get_db
from app.auth import get_current_user

from app.models.groupe import Groupe
from app.models.utilisateur_groupe import UtilisateurGroupe

from app.services.planning_auto import generer_planning_pour_utilisateur
from app.services.notifications import decide_and_create          # ⬅️ NOUVEL IMPORT

router = APIRouter()

# ─────────────────────────────  CRÉATION  ──────────────────────────────
@router.post("/taches/")
def create_tache(
    tache: TacheCreate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    if tache.groupe_id:
        groupe = db.query(Groupe).filter_by(id=tache.groupe_id).first()
        if not groupe:
            raise HTTPException(404, "Groupe introuvable")

        membres = db.query(UtilisateurGroupe).filter_by(groupe_id=tache.groupe_id).all()
        if not membres:
            raise HTTPException(400, "Aucun membre dans ce groupe")

        taches_creees = []
        for membre in membres:
            nouvelle = Tache(
                titre=tache.titre,
                description=tache.description,
                priorite=tache.priorite,
                date_echeance=tache.date_echeance,
                utilisateur_id=membre.utilisateur_id,
                groupe_id=tache.groupe_id
            )
            db.add(nouvelle)
            taches_creees.append(nouvelle)

        db.commit()

        # ➜ notifications + planning pour chaque membre
        for membre, nt in zip(membres, taches_creees):
            decide_and_create(db, nt)                        # ⬅️ NOTIFICATION
            generer_planning_pour_utilisateur(db, membre.utilisateur_id)

        return {"message": f"{len(taches_creees)} tâches créées pour le groupe."}

    # ─── tâche individuelle ───
    nouvelle = Tache(**tache.dict(), utilisateur_id=user.id)
    db.add(nouvelle)
    db.commit()
    db.refresh(nouvelle)

    decide_and_create(db, nouvelle)                          # ⬅️ NOTIFICATION
    generer_planning_pour_utilisateur(db, user.id)

    return nouvelle

# ─────────────────────────────  LECTURE  ───────────────────────────────
@router.get("/taches/{tache_id}")
def get_tache(
    tache_id: int,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    tache = db.query(Tache).filter(Tache.id == tache_id,
                                   Tache.utilisateur_id == user.id).first()
    if not tache:
        raise HTTPException(404, "Tâche non trouvée")
    return tache

# ───────────────────────  MISE À JOUR DU STATUT  ───────────────────────
@router.put("/taches/{tache_id}/statut")
def update_tache_statut(
    tache_id: int,
    statut_data: TacheStatutUpdate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    tache = db.query(Tache).filter(Tache.id == tache_id,
                                   Tache.utilisateur_id == user.id).first()
    if not tache:
        raise HTTPException(404, "Tâche non trouvée")

    tache.statut = statut_data.statut
    db.commit()
    db.refresh(tache)

    decide_and_create(db, tache)                             # ⬅️ NOTIFICATION
    generer_planning_pour_utilisateur(db, user.id)

    return tache

# ─────────────────────────────  MISE À JOUR  ───────────────────────────
@router.put("/taches/{tache_id}")
def update_tache(
    tache_id: int,
    updates: TacheUpdate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    tache = db.query(Tache).filter(Tache.id == tache_id,
                                   Tache.utilisateur_id == user.id).first()
    if not tache:
        raise HTTPException(404, "Tâche non trouvée")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(tache, key, value)

    db.commit()

    decide_and_create(db, tache)                             # ⬅️ NOTIFICATION
    generer_planning_pour_utilisateur(db, user.id)

    return tache

# ─────────────────────────────  SUPPRESSION  ───────────────────────────
@router.delete("/taches/{tache_id}")
def delete_tache(
    tache_id: int,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    tache = db.query(Tache).filter(Tache.id == tache_id,
                                   Tache.utilisateur_id == user.id).first()
    if not tache:
        raise HTTPException(404, "Tâche non trouvée")

    db.delete(tache)
    db.commit()

    # Pas de decide_and_create ici : la tâche n’existe plus,
    # mais on régénère le planning pour retirer son créneau
    generer_planning_pour_utilisateur(db, user.id)

    return {"message": "Tâche supprimée avec succès"}

# ─────────────────────────  LISTES CONVENIENTES  ───────────────────────
@router.get("/taches/")
def get_all_taches(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    return db.query(Tache).filter(Tache.utilisateur_id == user.id,
                                  Tache.statut == "En cours").all()

@router.get("/taches/terminees/")
def get_taches_terminees(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    return db.query(Tache).filter(Tache.utilisateur_id == user.id,
                                  Tache.statut == "Terminé").all()
