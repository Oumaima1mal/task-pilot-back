from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class Planning(Base):
    __tablename__ = "planning"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=False)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"))

    utilisateur = relationship("Utilisateur", back_populates="plannings")
    taches_planifiees = relationship("TachePlanifiee", back_populates="planning")
