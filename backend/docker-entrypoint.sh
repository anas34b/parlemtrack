#!/bin/sh
# Applique les migrations avant de démarrer l'API : au premier déploiement
# réel, "alembic upgrade head" avait dû être lancé à la main (voir BUG-013)
# faute de quoi le conteneur backend démarrait sur un schéma vide.
set -e

alembic upgrade head
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
