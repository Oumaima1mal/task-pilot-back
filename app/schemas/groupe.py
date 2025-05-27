from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional

class GroupeBase(BaseModel):
    nom: str
    description: str | None = None

class GroupeCreate(GroupeBase):
    pass

class GroupeOut(BaseModel):
    id: int
    nom: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
