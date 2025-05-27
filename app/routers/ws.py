from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from fastapi.websockets import WebSocketDisconnect
from jose import JWTError, jwt
from app.auth import SECRET_KEY, ALGORITHM
from app.websocket.manager import ws_manager
import logging

router = APIRouter()

# Configurer le logging pour les WebSockets
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str):
    user_id = None
    try:
        # Décoder le token JWT
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            if user_email is None:
                raise ValueError("Token invalide")
            
            # Ici vous devriez récupérer l'user_id depuis l'email
            # Pour l'instant, je vais utiliser l'email comme identifiant
            # Vous devrez adapter selon votre logique
            from app.database.db import SessionLocal
            from app.models.user import Utilisateur
            
            db = SessionLocal()
            try:
                user = db.query(Utilisateur).filter(Utilisateur.email == user_email).first()
                if not user:
                    raise ValueError("Utilisateur non trouvé")
                user_id = user.id
            finally:
                db.close()
                
        except (JWTError, ValueError) as e:
            logger.warning(f"Connexion WebSocket refusée: {str(e)}")
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connecter l'utilisateur
        await ws_manager.connect(ws, user_id)
        logger.info(f"Utilisateur {user_id} connecté via WebSocket")
        
        try:
            # Boucle de maintien de la connexion
            while True:
                # Recevoir les messages du client (ping/pong, keep-alive)
                message = await ws.receive_text()
                
                # Optionnel: traiter les messages spéciaux
                if message == "ping":
                    await ws.send_text("pong")
                elif message == "keep-alive":
                    await ws.send_text("alive")
                # Vous pouvez ajouter d'autres types de messages ici
                
        except WebSocketDisconnect:
            # Déconnexion normale du client - ne pas logger comme erreur
            logger.info(f"Utilisateur {user_id} déconnecté (WebSocket fermé par le client)")
            
        except Exception as e:
            # Autres erreurs inattendues
            logger.error(f"Erreur WebSocket pour l'utilisateur {user_id}: {str(e)}")
            
    except Exception as e:
        # Erreur lors de la connexion initiale
        logger.error(f"Erreur lors de l'établissement de la connexion WebSocket: {str(e)}")
        
    finally:
        # Nettoyer la connexion
        if user_id is not None:
            ws_manager.disconnect(user_id)
            logger.info(f"Connexion WebSocket nettoyée pour l'utilisateur {user_id}")