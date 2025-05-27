from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db 
from app.auth import get_current_user  # <--- importe le gestionnaire JWT
from app.models.utilisateur_groupe import UtilisateurGroupe
from app.schemas.utilisateur_groupe import UtilisateurGroupeCreate , UtilisateurGroupeRead , MembreDuGroupe
from app.models.user import Utilisateur
from app.models.groupe import Groupe
from app.models.tache import Tache
from app.schemas.tache import EtatTacheUtilisateur
from typing import List

router = APIRouter()

@router.post("/groupes/ajouter-membre")
def ajouter_membre(data: UtilisateurGroupeCreate, db: Session = Depends(get_db)):
    # Vérifie que l'utilisateur et le groupe existent
    utilisateur = db.query(Utilisateur).filter_by(id=data.utilisateur_id).first()
    groupe = db.query(Groupe).filter_by(id=data.groupe_id).first()
    if not utilisateur or not groupe:
        raise HTTPException(status_code=404, detail="Utilisateur ou groupe introuvable")

    # Vérifie que l'utilisateur n'est pas déjà membre
    existe = db.query(UtilisateurGroupe).filter_by(utilisateur_id=data.utilisateur_id, groupe_id=data.groupe_id).first()
    if existe:
        raise HTTPException(status_code=400, detail="L'utilisateur est déjà membre de ce groupe")

    membre = UtilisateurGroupe(**data.dict())
    db.add(membre)
    db.commit()
    return {"message": "Membre ajouté avec succès"}

# Route pour afficher la liste des membres 
# @router.get("/groupes/{groupe_id}/membres", response_model=List[UtilisateurGroupeRead])
# def get_membres_groupe(groupe_id: int, db: Session = Depends(get_db)):
#     """
#     Retourne tous les membres d'un groupe donné avec leur rôle.
#     """
#     groupe = db.query(Groupe).filter_by(id=groupe_id).first()
#     if not groupe:
#         raise HTTPException(status_code=404, detail="Groupe non trouvé")

#     membres = db.query(UtilisateurGroupe).filter_by(groupe_id=groupe_id).all()
#     return membres
# Route pour afficher la liste des membres 
@router.get("/groupes/{groupe_id}/membres", response_model=List[MembreDuGroupe])
def get_membres_du_groupe(
    groupe_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Vérification que le groupe existe
    groupe = db.query(Groupe).filter(Groupe.id == groupe_id).first()
    if not groupe:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")

    # Jointure pour récupérer les utilisateurs + rôle
    membres = (
        db.query(Utilisateur, UtilisateurGroupe.role)
        .join(UtilisateurGroupe, Utilisateur.id == UtilisateurGroupe.utilisateur_id)
        .filter(UtilisateurGroupe.groupe_id == groupe_id)
        .filter(Utilisateur.id != current_user.id)
        .all()
    )

    # Construire une liste de MembreDuGroupe
    membres_list = []
    for user, role in membres:
        membres_list.append(MembreDuGroupe(
            id=user.id,
            nom=user.nom,
            prenom=user.prenom,
            email=user.email,
            tel=user.tel,
            date_creation=user.date_creation,
            role=role
        ))

    return membres_list
#route pour afficher l'etat d'avancement des membres pour une tache 
@router.get("/groupe/{groupe_id}/tache/etat", response_model=list[EtatTacheUtilisateur])
def get_etat_tache(groupe_id: int, titre: str, db: Session = Depends(get_db)):
    resultats = (
        db.query(Utilisateur.nom, Utilisateur.prenom, Tache.statut)
        .join(Tache, Utilisateur.id == Tache.utilisateur_id)
        .filter(Tache.groupe_id == groupe_id, Tache.titre == titre)
        .all()
    )

    if not resultats:
        raise HTTPException(status_code=404, detail="Tâche introuvable ou aucun membre assigné.")

    return [
        EtatTacheUtilisateur(nom=nom, prenom=prenom, statut=statut)
        for nom, prenom, statut in resultats
    ]