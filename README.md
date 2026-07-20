# ParlemTrack

Tracker parlementaire français : données open data de l'Assemblée nationale et analyse IA neutre (Mistral), générée une seule fois par scrutin et stockée en base.

## Stack

Python 3.12 / FastAPI / SQLAlchemy 2.x / PostgreSQL 16 / Redis 7 / Next.js 14 (à venir en Phase 4).

## Installation

1. Copier le fichier d'environnement et compléter les valeurs si besoin :

```bash
cp .env.example .env
```

2. Démarrer PostgreSQL et Redis :

```bash
docker compose up -d
```

3. Créer l'environnement virtuel Python et installer les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Appliquer les migrations de base de données :

```bash
alembic upgrade head
```

## Lancement

Les commandes ci-dessous supposent le venv activé (`source .venv/bin/activate`).

```bash
# Pipeline de collecte (Phase 1)
python -m pipeline.run

# API (Phase 2)
uvicorn backend.app.main:app --reload
```

## Commandes utiles

Toujours avec le venv activé :

```bash
ruff check .              # lint Python
pytest --cov              # tests + couverture
docker compose down       # arrêter les services locaux
```

## Structure du projet

```
pipeline/    collecte, parsing et stockage des données AN
backend/     API FastAPI
frontend/    interface Next.js (Phase 4)
tests/       tests pytest (pipeline, backend) et fixtures
docs/        manuels, fiches de bugs, cahier de recettes
alembic/     migrations de base de données
scripts/     scripts d'exploitation (ex. génération du rendu ZIP)
```

Documentation complète : voir [docs/](docs/).
