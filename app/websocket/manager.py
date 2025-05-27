import asyncio
from typing import Dict
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class WSManager:
    def __init__(self):
        self.active: Dict[int, WebSocket] = {}   # {user_id: websocket}

    async def connect(self, ws: WebSocket, user_id: int):
        """Connecter un utilisateur"""
        try:
            await ws.accept()
            self.active[user_id] = ws
            logger.info(f"WebSocket connecté pour l'utilisateur {user_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la connexion WebSocket pour l'utilisateur {user_id}: {str(e)}")
            raise

    def disconnect(self, user_id: int):
        """Déconnecter un utilisateur"""
        if user_id in self.active:
            del self.active[user_id]
            logger.info(f"WebSocket déconnecté pour l'utilisateur {user_id}")

    async def push(self, user_id: int, payload: dict):
        """Envoyer un message à un utilisateur spécifique"""
        ws = self.active.get(user_id)
        if ws:
            try:
                await ws.send_json(payload)
                logger.debug(f"Message envoyé à l'utilisateur {user_id}: {payload}")
            except WebSocketDisconnect:
                # Connexion fermée côté client
                logger.info(f"WebSocket fermé côté client pour l'utilisateur {user_id}")
                self.disconnect(user_id)
            except Exception as e:
                # Autres erreurs de connexion
                logger.error(f"Erreur lors de l'envoi de message à l'utilisateur {user_id}: {str(e)}")
                self.disconnect(user_id)
        else:
            logger.debug(f"Aucune connexion WebSocket active pour l'utilisateur {user_id}")

    async def broadcast(self, payload: dict):
        """Envoyer un message à tous les utilisateurs connectés"""
        if not self.active:
            logger.debug("Aucune connexion WebSocket active pour le broadcast")
            return
            
        disconnected_users = []
        
        for user_id, ws in self.active.items():
            try:
                await ws.send_json(payload)
            except WebSocketDisconnect:
                disconnected_users.append(user_id)
            except Exception as e:
                logger.error(f"Erreur lors du broadcast à l'utilisateur {user_id}: {str(e)}")
                disconnected_users.append(user_id)
        
        # Nettoyer les connexions fermées
        for user_id in disconnected_users:
            self.disconnect(user_id)
            
        if disconnected_users:
            logger.info(f"Connexions nettoyées après broadcast: {disconnected_users}")

    def get_connected_users(self):
        """Retourner la liste des utilisateurs connectés"""
        return list(self.active.keys())

    def is_connected(self, user_id: int) -> bool:
        """Vérifier si un utilisateur est connecté"""
        return user_id in self.active

ws_manager = WSManager()     # instance unique à importer partout