from pydantic import BaseModel
from pydantic.config import ConfigDict
from datetime import datetime
from typing import Optional

class TacheCreate(BaseModel):
    titre: str
    description: Optional[str]
    priorite: str
    date_echeance: datetime
    groupe_id: Optional[int] = None
    

class TacheUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    date_echeance: Optional[datetime] = None
    statut: Optional[str] = None
    groupe_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")

class TacheStatutUpdate(BaseModel):
    statut: str

class EtatTacheUtilisateur(BaseModel):
    nom: str
    prenom: str
    statut: str