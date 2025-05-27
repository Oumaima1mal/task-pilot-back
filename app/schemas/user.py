from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict
from datetime import datetime

class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    mot_de_passe: str
    tel: str

class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class UtilisateurRead(BaseModel):
    id: int
    nom: str
    prenom: str
    email: EmailStr
    tel: str
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)

