import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import Utilisateur
from app.models.tache import Tache
from datetime import datetime, timedelta

# Configuration des emails
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "malikioumaima587@gmail.com"  # Remplacez par votre adresse email
EMAIL_HOST_PASSWORD = "lqjw kwyr cabk nydh"  # Remplacez par votre mot de passe
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "TaskPilot <malikioumaima587@gmail.com>"  # Remplacez par votre adresse

def generate_task_summary_html(db: Session, utilisateur_id: int):
    """
    Génère un récapitulatif HTML des tâches pour un utilisateur
    """
    now = datetime.utcnow()
    today = now.date()
    
    # Tâches en retard
    taches_retard = db.query(Tache).filter(
        Tache.utilisateur_id == utilisateur_id,
        Tache.statut != "Terminé",
        Tache.date_echeance < now
    ).all()
    
    # Tâches du jour
    taches_jour = db.query(Tache).filter(
        Tache.utilisateur_id == utilisateur_id,
        Tache.statut != "Terminé",
        Tache.date_echeance >= now,
        Tache.date_echeance < datetime(today.year, today.month, today.day, 23, 59, 59)
    ).all()
    
    # Tâches à venir (3 prochains jours)
    date_limite = now + timedelta(days=3)
    taches_a_venir = db.query(Tache).filter(
        Tache.utilisateur_id == utilisateur_id,
        Tache.statut != "Terminé",
        Tache.date_echeance > datetime(today.year, today.month, today.day, 23, 59, 59),
        Tache.date_echeance <= date_limite
    ).all()
    
    # Générer le HTML
    html = "<h2>Récapitulatif de vos tâches</h2>"
    
    if taches_retard:
        html += """
        <div style="margin-top: 15px;">
            <h3 style="color: #e11d48;">Tâches en retard</h3>
            <ul style="padding-left: 20px;">
        """
        for tache in taches_retard:
            html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{tache.titre}</strong>
                <div style="font-size: 14px; color: #64748b;">
                    Échéance: {tache.date_echeance.strftime('%d/%m/%Y à %H:%M')}
                </div>
            </li>
            """
        html += "</ul></div>"
    
    if taches_jour:
        html += """
        <div style="margin-top: 15px;">
            <h3 style="color: #0284c7;">Tâches pour aujourd'hui</h3>
            <ul style="padding-left: 20px;">
        """
        for tache in taches_jour:
            html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{tache.titre}</strong>
                <div style="font-size: 14px; color: #64748b;">
                    Échéance: {tache.date_echeance.strftime('%d/%m/%Y à %H:%M')}
                </div>
            </li>
            """
        html += "</ul></div>"
    
    if taches_a_venir:
        html += """
        <div style="margin-top: 15px;">
            <h3 style="color: #16a34a;">Tâches à venir</h3>
            <ul style="padding-left: 20px;">
        """
        for tache in taches_a_venir:
            html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{tache.titre}</strong>
                <div style="font-size: 14px; color: #64748b;">
                    Échéance: {tache.date_echeance.strftime('%d/%m/%Y à %H:%M')}
                </div>
            </li>
            """
        html += "</ul></div>"
    
    if not (taches_retard or taches_jour or taches_a_venir):
        html += """
        <div style="margin-top: 15px; padding: 10px; background-color: #f8fafc; border-radius: 5px; text-align: center;">
            <p>Vous n'avez aucune tâche en cours pour le moment.</p>
        </div>
        """
    
    return html

def send_email(to_email, subject, html_content):
    """
    Envoie un email avec le contenu HTML fourni - VERSION SYNCHRONE SIMPLIFIÉE
    """
    try:
        print(f"Préparation de l'email pour: {to_email}")
        print(f"Sujet: {subject}")
        
        msg = MIMEMultipart()
        msg['From'] = DEFAULT_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Ajouter le contenu HTML
        msg.attach(MIMEText(html_content, 'html'))
        
        print(f"Connexion au serveur SMTP: {EMAIL_HOST}:{EMAIL_PORT}")
        
        # Connexion au serveur SMTP avec timeout réduit
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        
        if EMAIL_USE_TLS:
            print("Démarrage de TLS...")
            server.starttls()
        
        # Authentification
        print(f"Authentification avec l'utilisateur: {EMAIL_HOST_USER}")
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Envoi de l'email
        print("Envoi de l'email...")
        server.send_message(msg)
        
        # Fermeture de la connexion
        print("Fermeture de la connexion SMTP...")
        server.quit()
        
        print(f"Email envoyé avec succès à {to_email}")
        return True
        
    except smtplib.SMTPException as e:
        print(f"Erreur SMTP lors de l'envoi de l'email: {str(e)}")
        return False
    except Exception as e:
        print(f"Erreur générale lors de l'envoi de l'email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_notification_email(db: Session, notification_id: int):
    """
    Version SYNCHRONE SIMPLIFIÉE pour envoyer un email de notification
    """
    try:
        print(f"Début de send_notification_email pour notification {notification_id}")
        
        # Récupérer la notification
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            print(f"Notification {notification_id} non trouvée")
            return False
        
        # Récupérer l'utilisateur
        utilisateur = db.query(Utilisateur).filter(Utilisateur.id == notification.utilisateur_id).first()
        if not utilisateur or not utilisateur.email:
            print(f"Utilisateur {notification.utilisateur_id} non trouvé ou sans email")
            return False
        
        print(f"Envoi d'email à: {utilisateur.email}")
        
        # Récupérer la tâche associée si elle existe
        tache = None
        tache_info = ""
        if notification.tache_id:
            tache = db.query(Tache).filter(Tache.id == notification.tache_id).first()
            if tache:
                tache_info = f"""
                <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                    <p><strong>Tâche:</strong> {tache.titre}</p>
                    <p><strong>Description:</strong> {tache.description or 'Aucune description'}</p>
                    <p><strong>Échéance:</strong> {tache.date_echeance.strftime('%d/%m/%Y à %H:%M') if tache.date_echeance else 'Non définie'}</p>
                    <p><strong>Priorité:</strong> {tache.priorite}</p>
                </div>
                """
        
        # Générer le récapitulatif des tâches si c'est un email quotidien
        task_summary = ""
        if "Récapitulatif" in notification.contenu:
            task_summary = f"""
            <div style="margin-top: 20px;">
                {generate_task_summary_html(db, notification.utilisateur_id)}
            </div>
            """
        
        # Créer le contenu HTML de l'email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Notification TaskPilot</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6d28d9; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 20px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 0 0 5px 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #6b7280; text-align: center; }}
                .button {{ display: inline-block; background-color: #6d28d9; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Notification TaskPilot</h2>
                </div>
                <div class="content">
                    <p>Bonjour {utilisateur.nom if hasattr(utilisateur, 'nom') else utilisateur.email},</p>
                    
                    <p>{notification.contenu}</p>
                    
                    {tache_info}
                    
                    {task_summary}
                    
                    <p style="margin-top: 20px;">
                        <a href="http://localhost:8081/taches" class="button">Voir mes tâches</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par TaskPilot. Merci de ne pas y répondre.</p>
                    <p>© {datetime.now().year} TaskPilot. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Sujet de l'email
        subject = f"TaskPilot - {notification.contenu[:50]}{'...' if len(notification.contenu) > 50 else ''}"
        
        # Envoyer l'email
        success = send_email(utilisateur.email, subject, html_content)
        
        print(f"Résultat de l'envoi d'email: {'SUCCÈS' if success else 'ÉCHEC'}")
        return success
        
    except Exception as e:
        print(f"Erreur dans send_notification_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_email_service():
    """
    Fonction de test pour vérifier la configuration email
    """
    try:
        print("Test de la configuration email...")
        
        # Test simple d'envoi d'email
        test_html = """
        <html>
        <body>
            <h2>Test Email TaskPilot</h2>
            <p>Ceci est un email de test pour vérifier la configuration.</p>
            <p>Si vous recevez cet email, la configuration fonctionne!</p>
        </body>
        </html>
        """
        
        # Remplacez par votre email de test
        test_email = "votre-email-test@gmail.com"
        
        success = send_email(test_email, "Test TaskPilot", test_html)
        return success
        
    except Exception as e:
        print(f"Erreur dans test_email_service: {str(e)}")
        return False