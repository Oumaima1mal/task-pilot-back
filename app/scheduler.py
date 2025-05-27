# app/scheduler.py
from datetime import datetime
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.database.db import SessionLocal
from app.models.tache import Tache
from app.models.notification import Notification
from app.services.notifications import decide_and_create

scheduler = AsyncIOScheduler()

def scan_echeances():
    """
    Parcourt les tâches non terminées et déclenche decide_and_create.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        print(f"Scan des échéances à {now}")
        
        # Vérifier les tâches à venir
        taches_a_venir = db.query(Tache).filter(
            Tache.statut != "Terminé",
            Tache.date_echeance > now
        ).all()
        print(f"Tâches à venir trouvées: {len(taches_a_venir)}")
        
        for tache in taches_a_venir:
            decide_and_create(db, tache)
            
        # Vérifier les tâches en retard
        taches_en_retard = db.query(Tache).filter(
            Tache.statut != "Terminé",
            Tache.date_echeance <= now
        ).all()
        print(f"Tâches en retard trouvées: {len(taches_en_retard)}")
        
        for tache in taches_en_retard:
            decide_and_create(db, tache)
            
    except Exception as e:
        print(f"Erreur dans scan_echeances: {str(e)}")
    finally:
        db.close()

def envoyer_emails_en_attente():
    """
    Parcourt les notifications de type email non envoyées et les envoie.
    """
    db: Session = SessionLocal()
    try:
        print("Vérification des emails en attente...")
        
        # Récupérer les notifications de type email non envoyées
        notifications = db.query(Notification).filter(
            Notification.type_notification == "email",
            Notification.est_lue == False
        ).all()
        
        print(f"Notifications email en attente: {len(notifications)}")
        
        for notification in notifications:
            print(f"Traitement de la notification email {notification.id}")
            
            # Envoyer l'email
            from app.services.email_service import send_notification_email
            success = send_notification_email(db, notification.id)
            
            # Si l'email a été envoyé avec succès, marquer la notification comme lue
            if success:
                notification.est_lue = True
                notification.date_lecture = datetime.utcnow()
                db.commit()
                print(f"Email {notification.id} envoyé et marqué comme lu")
            else:
                print(f"Échec de l'envoi de l'email {notification.id}")
                
    except Exception as e:
        print(f"Erreur dans envoyer_emails_en_attente: {str(e)}")
    finally:
        db.close()

def envoyer_rappels_quotidiens():
    """
    Envoie un récapitulatif quotidien des tâches à faire pour chaque utilisateur.
    """
    db: Session = SessionLocal()
    try:
        print("Envoi des rappels quotidiens...")
        
        # Récupérer tous les utilisateurs
        from app.models.user import Utilisateur
        utilisateurs = db.query(Utilisateur).all()
        
        now = datetime.utcnow()
        today = now.date()
        
        for utilisateur in utilisateurs:
            print(f"Traitement des rappels pour l'utilisateur {utilisateur.id}")
            
            # Récupérer les tâches du jour pour cet utilisateur
            taches_jour = db.query(Tache).filter(
                Tache.utilisateur_id == utilisateur.id,
                Tache.statut != "Terminé",
                Tache.date_echeance >= now,
                Tache.date_echeance < datetime(today.year, today.month, today.day, 23, 59, 59)
            ).all()
            
            # Récupérer les tâches en retard pour cet utilisateur
            taches_retard = db.query(Tache).filter(
                Tache.utilisateur_id == utilisateur.id,
                Tache.statut != "Terminé",
                Tache.date_echeance < now
            ).all()
            
            # S'il y a des tâches à faire aujourd'hui ou en retard, créer une notification
            if taches_jour or taches_retard:
                print(f"Création d'un rappel quotidien pour l'utilisateur {utilisateur.id}")
                
                # Construire le contenu de la notification
                contenu = f"Récapitulatif de vos tâches pour aujourd'hui ({today.strftime('%d/%m/%Y')})"
                
                # Vérifier si un rappel quotidien a déjà été envoyé aujourd'hui
                existing_reminder = db.query(Notification).filter(
                    Notification.utilisateur_id == utilisateur.id,
                    Notification.contenu.like("Récapitulatif de vos tâches%"),
                    Notification.type_notification == "email",
                    Notification.date_envoi >= datetime(today.year, today.month, today.day)
                ).first()
                
                if existing_reminder:
                    print(f"Rappel quotidien déjà envoyé pour l'utilisateur {utilisateur.id}")
                    continue
                
                # Créer une notification
                notif = Notification(
                    contenu=contenu,
                    type_notification="email",
                    utilisateur_id=utilisateur.id,
                    est_lue=False,
                    date_envoi=now
                )
                db.add(notif)
                db.commit()
                db.refresh(notif)
                
                # Envoyer l'email
                from app.services.email_service import send_notification_email
                success = send_notification_email(db, notif.id)
                
                if success:
                    notif.est_lue = True
                    notif.date_lecture = datetime.utcnow()
                    db.commit()
                    print(f"Rappel quotidien envoyé pour l'utilisateur {utilisateur.id}")
                else:
                    print(f"Échec de l'envoi du rappel quotidien pour l'utilisateur {utilisateur.id}")
                
    except Exception as e:
        print(f"Erreur dans envoyer_rappels_quotidiens: {str(e)}")
    finally:
        db.close()

def start_scheduler():
    print("Démarrage du scheduler...")
    
    # Exécuter immédiatement au démarrage
    scan_echeances()
    
    # Vérifier les échéances toutes les 15 minutes
    scheduler.add_job(
        scan_echeances,
        trigger=IntervalTrigger(minutes=15),
        id="scan_echeances",
        replace_existing=True,
    )
    
    # Envoyer les emails en attente toutes les 2 minutes (plus fréquent pour les tests)
    scheduler.add_job(
        envoyer_emails_en_attente,
        trigger=IntervalTrigger(minutes=2),
        id="envoyer_emails",
        replace_existing=True,
    )
    
    # Envoyer les rappels quotidiens à 8h du matin
    scheduler.add_job(
        envoyer_rappels_quotidiens,
        trigger=CronTrigger(hour=8, minute=0),
        id="rappels_quotidiens",
        replace_existing=True,
    )
    
    scheduler.start()
    print("Scheduler démarré avec succès!")