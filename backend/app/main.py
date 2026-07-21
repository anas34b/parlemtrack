"""Point d'entrée de l'API FastAPI ParlemTrack.

Lancement : `uvicorn backend.app.main:app`
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.app.api.routes import actualites, deputes, groupes, health, recherche, scrutins
from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from backend.app.core.security import HeadersSecuriteMiddleware, limiter

setup_logging()
settings = get_settings()

app = FastAPI(
    title="ParlemTrack",
    description="API citoyenne des votes de l'Assemblée nationale, avec analyse IA neutre.",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# SlowAPIMiddleware seul n'applique pas fiablement default_limits sur FastAPI :
# chaque route est aussi décorée avec @limiter.limit() (voir api/routes/*.py),
# qui est le mécanisme qui déclenche réellement le comptage/429 (vérifié en réel).
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(HeadersSecuriteMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(scrutins.router)
app.include_router(deputes.router)
app.include_router(groupes.router)
app.include_router(recherche.router)
app.include_router(actualites.router)
