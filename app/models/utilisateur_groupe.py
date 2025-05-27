from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class UtilisateurGroupe(Base):
    __tablename__ = "utilisateur_groupe"

    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id", ondelete="CASCADE"), primary_key=True)
    groupe_id = Column(Integer, ForeignKey("groupe.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(50), default="Membre", nullable=False)

    utilisateur = relationship("Utilisateur", back_populates="groupes_associes")
    groupe = relationship("Groupe", back_populates="membres_associes")
