from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class Tache(Base):
    __tablename__ = "tache"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text)
    priorite = Column(String(50))
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_echeance = Column(DateTime, nullable=False)
    statut = Column(String(50), default="En cours")
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"))
    groupe_id = Column(Integer, ForeignKey("groupe.id"), nullable=True)

    utilisateur = relationship("Utilisateur", back_populates="taches")
    groupe = relationship("Groupe", back_populates="taches")
    
