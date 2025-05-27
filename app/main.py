from fastapi import FastAPI
from app.routers import auth
from app.database.db import Base, engine
from app.routers import tache
from app.routers import groupe
from app.routers import utilisateur_groupe
from app.routers import planning
from app.routers import tache_planifiee
from app.routers import utilisateur_routes
from app.routers import planning_auto
from fastapi.middleware.cors import CORSMiddleware
from app.scheduler import start_scheduler
from app.routers import notification
from app.routers import health_check
from app.routers import ws


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Démarrage du scheduler...")
    start_scheduler()
    print("Scheduler démarré avec succès!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://task-pilot-pi.vercel.app"],  # ou ["*"] en dev si tu veux tout autoriser
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tache.router)
app.include_router(groupe.router)
app.include_router(utilisateur_groupe.router)
app.include_router(planning.router)
app.include_router(tache_planifiee.router)
app.include_router(utilisateur_routes.router)
app.include_router(planning_auto.router)
app.include_router(notification.router)
app.include_router(health_check.router)
app.include_router(ws.router)

