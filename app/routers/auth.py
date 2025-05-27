from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.database.db import SessionLocal
from app.models.user import Utilisateur
from app.schemas.user import UtilisateurCreate, UtilisateurLogin
from app.auth import create_access_token
from app.models.planning import Planning
from app.services.planning_auto import generer_planning_pour_utilisateur
import datetime         
from sqlalchemy import func




router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: UtilisateurCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    hashed_pwd = bcrypt.hash(user.mot_de_passe)
    nouveau_user = Utilisateur(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        mot_de_passe=hashed_pwd,
        tel=user.tel
    )
    try:
        db.add(nouveau_user)
        db.commit()
        db.refresh(nouveau_user)

        # 🧪 Ajout pour affichage
        print("✅ Utilisateur inséré !")
        print("ID :", nouveau_user.id)
        print("Nom :", nouveau_user.nom)
        print("Email :", nouveau_user.email)
        print("Date de création :", nouveau_user.date_creation)
    except Exception as e:
        db.rollback()  # Annule les changements en cas d'erreur
        print(f"Erreur lors de l'ajout à la BDD : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
    
    return {"message": "Utilisateur enregistré avec succès"}

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    mot_de_passe = data.get("mot_de_passe")

    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user or not bcrypt.verify(mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide")
    # ─── Génération / mise à jour du planning ───
    today = datetime.date.today()

    deja = (
        db.query(Planning)
        .filter(
            Planning.utilisateur_id == user.id,
            func.date(Planning.date_debut) == today   # ⬅️ extraction de la partie “date” en SQL
        )
        .first()
    )

    if not deja:
        generer_planning_pour_utilisateur(db, user.id)

    # ─── JWT ───

    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

