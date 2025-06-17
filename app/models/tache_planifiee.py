from sqlalchemy import Column, Integer, ForeignKey, DateTime, Interval
from sqlalchemy.orm import relationship
from app.database.db import Base

class TachePlanifiee(Base):
    __tablename__ = "tacheplanifiee"

    id = Column(Integer, primary_key=True, index=True)
    tache_id = Column(Integer, ForeignKey("tache.id", ondelete="CASCADE"))
    date_debut = Column(DateTime, nullable=False)
    duree = Column(Interval, nullable=False)
    planning_id = Column(Integer, ForeignKey("planning.id"))

    tache = relationship("Tache")
    planning = relationship("Planning")
