from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.db import get_db
from app.models.notification import Notification
from app.auth import get_current_user
from app.services.email_service import send_notification_email
from app.services.email_service import send_email  # Importez la fonction send_email


router = APIRouter()

@router.get("/notifications/")
def get_notifications(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Correction: utiliser date_envoi au lieu de date_creation
    notifications = db.query(Notification).filter(Notification.utilisateur_id == user.id).order_by(Notification.date_envoi.desc()).all()
    if not notifications:
        return []
    return notifications

@router.put("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.utilisateur_id == user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    # Correction: utiliser est_lue au lieu de est_lu
    notification.est_lue = True
    notification.date_lecture = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    
    return notification

@router.put("/notifications/read-all")
def mark_all_notifications_as_read(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Correction: utiliser est_lue au lieu de est_lu
    notifications = db.query(Notification).filter(
        Notification.utilisateur_id == user.id,
        Notification.est_lue == False
    ).all()
    
    for notification in notifications:
        notification.est_lue = True
        notification.date_lecture = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"{len(notifications)} notifications marquées comme lues"}

@router.post("/notifications/send-test-email")
def send_test_email(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Endpoint pour tester l'envoi d'emails
    """
    # Créer une notification de test
    notif = Notification(
        contenu=f"Ceci est un email de test envoyé le {datetime.utcnow().strftime('%d/%m/%Y à %H:%M')}",
        type_notification="email",
        utilisateur_id=user.id,
        est_lue=False,
        date_envoi=datetime.utcnow()
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    
    # Envoyer l'email en arrière-plan
    background_tasks.add_task(send_notification_email, db, notif.id)
    
    return {"message": "Email de test en cours d'envoi", "notification_id": notif.id}

@router.get("/notifications/email/{notification_id}")
def resend_email_notification(notification_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Endpoint pour renvoyer un email pour une notification existante
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.utilisateur_id == user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    # Envoyer l'email en arrière-plan
    background_tasks.add_task(send_notification_email, db, notification.id)
    
    return {"message": "Email en cours d'envoi", "notification_id": notification.id}
@router.post("/notifications/test-email")
def test_email(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Endpoint pour tester l'envoi d'emails
    """
    from app.services.email_service import test_email_service
    
    success = test_email_service()
    
    if success:
        return {"message": "Email de test envoyé avec succès"}
    else:
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email de test")
@router.post("/test-email")
def test_email(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Route pour tester l'envoi d'emails
    """
    try:
        # Récupérer l'email de l'utilisateur
        email = user.email
        if not email:
            raise HTTPException(status_code=400, detail="L'utilisateur n'a pas d'adresse email")
        
        # Créer le contenu HTML de l'email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Email TaskPilot</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6d28d9; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 20px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 0 0 5px 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #6b7280; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Test Email TaskPilot</h2>
                </div>
                <div class="content">
                    <p>Bonjour {user.nom if hasattr(user, 'nom') else email},</p>
                    
                    <p>Ceci est un email de test envoyé depuis TaskPilot.</p>
                    
                    <p>Date et heure de l'envoi: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
                    
                    <p>Si vous recevez cet email, cela signifie que la configuration de l'envoi d'emails fonctionne correctement!</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par TaskPilot. Merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Importer les paramètres de configuration email
        from app.services.email_service import EMAIL_HOST_USER, DEFAULT_FROM_EMAIL
        
        # Afficher les informations de débogage
        print(f"Tentative d'envoi d'email à: {email}")
        print(f"De: {DEFAULT_FROM_EMAIL}")
        print(f"Utilisateur SMTP: {EMAIL_HOST_USER}")
        
        # Envoyer l'email
        success = send_email(
            email,
            "Test Email TaskPilot",
            html_content
        )
        
        if success:
            print("Email envoyé avec succès!")
            return {"status": "success", "message": "Email envoyé avec succès! Vérifiez votre boîte de réception."}
        else:
            print("Échec de l'envoi de l'email.")
            return {"status": "error", "message": "Échec de l'envoi de l'email. Vérifiez les logs pour plus d'informations."}
            
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi de l'email: {str(e)}")
@router.post("/notifications/force-check-overdue")
def force_check_overdue_endpoint(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Endpoint pour forcer la vérification des tâches en retard
    """
    try:
        from app.services.notifications import force_check_overdue_tasks
        force_check_overdue_tasks()
        return {"message": "Vérification forcée des tâches en retard terminée. Consultez les logs."}
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

@router.post("/notifications/diagnostic")
def diagnostic_endpoint(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """
    Endpoint pour lancer le diagnostic
    """
    try:
        from app.services.notifications import diagnostic_complet
        diagnostic_complet()
        return {"message": "Diagnostic terminé. Consultez les logs."}
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}