from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Literal

class UtilisateurGroupeCreate(BaseModel):
    utilisateur_id: int
    groupe_id: int
    role: Literal["Membre", "Admin"] = "Membre"

class UtilisateurGroupeRead(BaseModel):
    utilisateur_id: int
    groupe_id: int
    role: str

    model_config = ConfigDict(from_attributes=True)
class MembreDuGroupe(BaseModel):
    id: int
    nom: str
    prenom: str
    role: str  # <-- ajouté ici
    model_config = ConfigDict(from_attributes=True)