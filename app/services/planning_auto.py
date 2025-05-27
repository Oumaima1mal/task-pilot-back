from datetime import datetime, timedelta
from app.models.planning import Planning
from app.models.tache_planifiee import TachePlanifiee
from app.models.tache import Tache

def generer_planning_pour_utilisateur(db, utilisateur_id: int):
    # Déterminer les bornes de la journée actuelle
    aujourd_hui = datetime.now().date()
    date_debut = datetime.combine(aujourd_hui, datetime.min.time()).replace(hour=8)
    date_fin = date_debut + timedelta(hours=10)

    # Supprimer le planning existant pour aujourd'hui s'il existe
    planning_existant = db.query(Planning).filter(
        Planning.utilisateur_id == utilisateur_id,
        Planning.date_debut >= date_debut,
        Planning.date_debut < date_debut + timedelta(days=1)
    ).first()

    if planning_existant:
        # Supprimer les tâches planifiées associées
        db.query(TachePlanifiee).filter(TachePlanifiee.planning_id == planning_existant.id).delete()
        # Supprimer le planning
        db.delete(planning_existant)
        db.commit()

    # Récupérer les tâches non terminées
    taches = db.query(Tache).filter(
        Tache.utilisateur_id == utilisateur_id,
        Tache.statut != "terminée"
    ).all()

    # Trier par priorité et date d’échéance
    priorite_map = {"Urgent": 1, "Important": 2, "Facultatif": 3}
    taches.sort(key=lambda t: (priorite_map.get(t.priorite, 99), t.date_echeance))

    # Créer un nouveau planning
    planning = Planning(
        titre=f"Planning du {date_debut.date()}",
        date_debut=date_debut,
        date_fin=date_fin,
        utilisateur_id=utilisateur_id
    )
    db.add(planning)
    db.commit()
    db.refresh(planning)

    # Planifier les tâches
    heure_courante = date_debut
    for tache in taches:
        duree = timedelta(hours=1)  # à personnaliser selon la tâche
        if heure_courante + duree > date_fin:
            break  # Fin du créneau de planification

        tache_planifiee = TachePlanifiee(
            tache_id=tache.id,
            date_debut=heure_courante,
            duree=duree,
            planning_id=planning.id
        )
        db.add(tache_planifiee)
        heure_courante += duree

    db.commit()
    return planning
