from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    Boolean,
    String,
    ForeignKey,
)
from app.database.db import Base

class Notification(Base):
    __tablename__ = "notification"

    id               = Column(Integer, primary_key=True, index=True)
    contenu          = Column(Text, nullable=False)
    date_envoi       = Column(DateTime, default=datetime.utcnow, nullable=False)
    est_lue          = Column(Boolean, default=False)
    type_notification = Column(String(50), nullable=False)      # "websocket" / "email"
    # Suppression de window_label qui n'existe pas dans la base de données
    utilisateur_id   = Column(Integer, ForeignKey("utilisateur.id"))
    tache_id         = Column(Integer, ForeignKey("tache.id"))