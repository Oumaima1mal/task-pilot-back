from pydantic import BaseModel
from datetime import datetime

class PlanningCreate(BaseModel):
    titre: str
    date_debut: datetime
    date_fin: datetime

class PlanningOut(BaseModel):
    id: int
    titre: str
    date_debut: datetime
    date_fin: datetime

class Config:
    from_attributes = True
