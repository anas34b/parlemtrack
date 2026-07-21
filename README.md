# ParlemTrack

Tracker parlementaire français : données open data de l'Assemblée nationale et analyse IA neutre (Mistral), générée une seule fois par scrutin et stockée en base.

## Stack

Python 3.12 / FastAPI / SQLAlchemy 2.x / PostgreSQL 16 / Redis 7 / Next.js 14+ (App Router, TypeScript, PWA).

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
# Pipeline de collecte (Phase 1) : télécharge, parse et stocke scrutins,
# députés, groupes et scores Datan ; met à jour le cache RSS des actualités
python -m pipeline.run

# API (Phase 2) : documentation interactive sur http://localhost:8000/docs
uvicorn backend.app.main:app --reload
```

Frontend (dans un second terminal, sans le venv Python) :

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000, branché sur l'API ci-dessus
```

## Commandes utiles

Toujours avec le venv activé :

```bash
ruff check .                          # lint Python
pytest --cov                          # tous les tests + couverture
pytest tests/pipeline --cov=pipeline  # tests du pipeline seul (base PostgreSQL de test requise)
pytest tests/backend --cov=backend    # tests de l'API seule (base PostgreSQL de test requise)
docker compose down                   # arrêter les services locaux
```

Les tests du pipeline (`tests/pipeline/`) et de l'API (`tests/backend/`)
créent automatiquement une base PostgreSQL de test dédiée (`<nom_base>_test`)
au premier lancement, distincte de la base de développement — aucune donnée
réelle collectée n'est jamais lue ni modifiée par les suites de tests.

## Structure du projet

```
pipeline/    collecte, parsing, stockage et analyse IA des données AN
backend/     API FastAPI
frontend/    interface Next.js (App Router, TypeScript, PWA)
tests/       tests pytest (pipeline, backend) et fixtures
docs/        manuels, fiches de bugs, cahier de recettes
alembic/     migrations de base de données
scripts/     scripts d'exploitation (ex. génération du rendu ZIP)
```

Documentation complète : voir [docs/](docs/).
