# Version sécurisée pour les notifications WebSocket
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from app.websocket.manager import ws_manager
from app.database.db import SessionLocal
import logging

logger = logging.getLogger(__name__)

WINDOWS = (
    (timedelta(hours=24),  "24h"),
    (timedelta(hours=3),   "3h"),
    (timedelta(hours=1),   "1h"),
)

def decide_and_create(db: Session, tache) -> None:
    """
    Version sécurisée avec gestion d'erreurs WebSocket
    """
    try:
        now = datetime.utcnow()
        delta = tache.date_echeance - now
        
        print(f"Traitement de la tâche: {tache.titre} (ID: {tache.id})")
        
        # Vérifier si la tâche est en retard
        if delta < timedelta():
            print(f"Tâche en retard détectée: {tache.titre}")
            _create_notification_for_overdue_safe(db, tache)
            return
        
        # Vérifier si la tâche approche de son échéance
        for limit, label in WINDOWS:
            if timedelta() < delta <= limit:
                print(f"Tâche approchant de l'échéance: {tache.titre} ({label})")
                _create_if_not_exists_safe(db, tache, label)
                break
                
    except Exception as e:
        logger.error(f"Erreur dans decide_and_create: {str(e)}")

def _create_if_not_exists_safe(db: Session, tache, label: str):
    """
    Version sécurisée pour les tâches approchant de l'échéance
    """
    try:
        # Créer notification WebSocket
        content_ws = f"⏰ «{tache.titre}» arrive ({label} avant échéance)"
        
        # Vérifier si notification WebSocket existe déjà
        exists_ws = db.query(Notification).filter_by(
            tache_id=tache.id,
            contenu=content_ws,
            type_notification="websocket"
        ).first()
        
        if not exists_ws:
            notif_ws = Notification(
                contenu=content_ws,
                type_notification="websocket",
                utilisateur_id=tache.utilisateur_id,
                tache_id=tache.id,
                est_lue=False,
                date_envoi=datetime.utcnow()
            )
            db.add(notif_ws)
            db.commit()
            db.refresh(notif_ws)
            print(f"Notification WebSocket créée: {notif_ws.id}")
            
            # Push WebSocket de manière sécurisée
            _safe_websocket_push(notif_ws)

        # Créer notification Email pour tâches prioritaires
        if tache.priorite in ("Urgent", "Important"):
            _create_email_notification_safe(tache, f"⚠️ Rappel important: «{tache.titre}» arrive ({label} avant échéance)")
            
    except Exception as e:
        logger.error(f"Erreur dans _create_if_not_exists_safe: {str(e)}")

def _create_notification_for_overdue_safe(db: Session, tache):
    """
    Version sécurisée pour les tâches en retard
    """
    try:
        # Créer notification WebSocket
        content_ws = f"⚠️ «{tache.titre}» est en retard !"
        
        # Vérifier si notification WebSocket existe déjà
        exists_ws = db.query(Notification).filter_by(
            tache_id=tache.id,
            contenu=content_ws,
            type_notification="websocket"
        ).first()
        
        if not exists_ws:
            notif_ws = Notification(
                contenu=content_ws,
                type_notification="websocket",
                utilisateur_id=tache.utilisateur_id,
                tache_id=tache.id,
                est_lue=False,
                date_envoi=datetime.utcnow()
            )
            db.add(notif_ws)
            db.commit()
            db.refresh(notif_ws)
            print(f"Notification WebSocket créée pour tâche en retard: {notif_ws.id}")
            
            # Push WebSocket de manière sécurisée
            _safe_websocket_push(notif_ws)

        # Créer notification email pour les tâches en retard
        print(f"Création d'une notification email pour tâche en retard: {tache.titre}")
        _create_email_notification_safe(tache, f"🚨 ALERTE: «{tache.titre}» est en retard !")
        
    except Exception as e:
        logger.error(f"Erreur dans _create_notification_for_overdue_safe: {str(e)}")

def _safe_websocket_push(notification):
    """
    Fonction sécurisée pour envoyer des notifications WebSocket
    """
    try:
        # Vérifier si l'utilisateur est connecté
        if ws_manager.is_connected(notification.utilisateur_id):
            # Créer la tâche asyncio de manière sécurisée
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Si on est dans un contexte asyncio, créer la tâche
                    asyncio.create_task(
                        ws_manager.push(
                            notification.utilisateur_id, 
                            NotificationOut.from_orm(notification).dict()
                        )
                    )
                else:
                    # Si pas de loop actif, ignorer silencieusement
                    logger.debug(f"Pas de loop asyncio actif pour l'envoi WebSocket à l'utilisateur {notification.utilisateur_id}")
            except RuntimeError:
                # Pas de loop asyncio disponible, ignorer silencieusement
                logger.debug(f"Pas de loop asyncio disponible pour l'envoi WebSocket à l'utilisateur {notification.utilisateur_id}")
        else:
            logger.debug(f"Utilisateur {notification.utilisateur_id} non connecté via WebSocket")
            
    except Exception as e:
        # Ne pas faire échouer le processus principal si WebSocket échoue
        logger.warning(f"Erreur lors de l'envoi WebSocket (ignorée): {str(e)}")

def _create_email_notification_safe(tache, content: str):
    """
    Version sécurisée pour créer et envoyer une notification email
    """
    email_db = SessionLocal()
    try:
        print(f"Création d'une notification email: {content}")
        
        # Vérifier si une notification email similaire existe déjà AUJOURD'HUI
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day)
        
        exists = email_db.query(Notification).filter(
            Notification.tache_id == tache.id,
            Notification.type_notification == "email",
            Notification.date_envoi >= today_start,
            Notification.contenu.like(f"%{tache.titre}%")
        ).first()
        
        if exists:
            print(f"Notification email déjà envoyée aujourd'hui pour la tâche {tache.id}")
            return False
        
        # Créer la notification email
        email_notif = Notification(
            contenu=content,
            type_notification="email",
            utilisateur_id=tache.utilisateur_id,
            tache_id=tache.id,
            est_lue=False,
            date_envoi=datetime.utcnow()
        )
        email_db.add(email_notif)
        email_db.commit()
        email_db.refresh(email_notif)
        
        print(f"Notification Email créée avec l'ID: {email_notif.id}")
        
        # Envoyer l'email immédiatement
        from app.services.email_service import send_notification_email
        print(f"Tentative d'envoi d'email pour la notification {email_notif.id}")
        
        success = send_notification_email(email_db, email_notif.id)
        
        if success:
            print(f"✅ Email envoyé avec succès pour la notification {email_notif.id}")
            # Marquer comme envoyé
            email_notif.est_lue = True
            email_notif.date_lecture = datetime.utcnow()
            email_db.commit()
            return True
        else:
            print(f"❌ Échec de l'envoi d'email pour la notification {email_notif.id}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la création/envoi de notification email: {str(e)}")
        email_db.rollback()
        return False
    finally:
        email_db.close()