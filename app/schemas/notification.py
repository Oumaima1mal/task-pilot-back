from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NotificationBase(BaseModel):
    id: int
    contenu: str
    date_envoi: datetime
    est_lue: bool
    type_notification: str
    window_label: Optional[str] = None
    tache_id: Optional[int] = None

    class Config:
        from_attributes = True


class NotificationOut(NotificationBase):
    """Pour renvoyer au front (identique ici mais on garde la marge d’évol)."""
    pass
