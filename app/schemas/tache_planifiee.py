from datetime import datetime, timedelta
from pydantic import BaseModel

class TachePlanifieeBase(BaseModel):
    tache_id: int
    date_debut: datetime
    duree: timedelta
    planning_id: int

class TachePlanifieeCreate(TachePlanifieeBase):
    pass

class TachePlanifieeUpdate(BaseModel):
    date_debut: datetime
    duree: timedelta

class TachePlanifieeOut(TachePlanifieeBase):
    id: int

    class Config:
        from_attributes = True
