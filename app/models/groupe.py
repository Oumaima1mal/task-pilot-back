from sqlalchemy import Column, Integer, String, Text
from app.database.db import Base
from sqlalchemy.orm import relationship
 # Assurez-vous que `Base` vient de votre fichier de connexion DB

class Groupe(Base):
    __tablename__ = "groupe"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    taches = relationship("Tache", back_populates="groupe")
    membres_associes = relationship("UtilisateurGroupe", back_populates="groupe", cascade="all, delete-orphan")
