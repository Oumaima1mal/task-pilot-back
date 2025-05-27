from sqlalchemy import Column, Integer, String, DateTime
from app.database.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    mot_de_passe = Column(String(255), nullable=False)
    tel = Column(String(50), nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)

    taches = relationship("Tache", back_populates="utilisateur", lazy="joined")
    groupes_associes = relationship("UtilisateurGroupe", back_populates="utilisateur", cascade="all, delete-orphan")
    plannings = relationship("Planning", back_populates="utilisateur")


