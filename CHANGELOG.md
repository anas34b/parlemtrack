# Changelog — ParlemTrack

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).
Aucune version n'est encore taguée : tout l'historique ci-dessous est
regroupé par phase de développement, dans l'ordre chronologique réel
(`git log`).

## [Non publié]

### Phase 5 — CI/CD et déploiement (2026-07-22 → 2026-07-23)

#### Ajouté
- Job frontend (lint, test, build) dans la CI, en plus du job backend.
- Workflow `pipeline-collecte.yml` : cron nocturne de collecte, exécuté
  via SSH dans le conteneur backend du VPS, avec notification par issue
  GitHub en cas d'échec.
- Workflow `deploy.yml` : déploiement automatique sur push `main`.
- Images Docker de production (`backend/Dockerfile`, `frontend/Dockerfile`,
  multi-stage, utilisateurs non-root) et `docker-compose.prod.yml`
  (backend, frontend, PostgreSQL, Redis), testés réellement en local.
- `backend/docker-entrypoint.sh` : application automatique des migrations
  Alembic au démarrage du conteneur backend.
- Manuel de déploiement (`docs/manuels/deploiement.md`).

#### Modifié
- Backoff du rate limit Mistral porté à 30 s (15 s insuffisant en pratique).
- Architecture de déploiement simplifiée à un seul environnement
  (`~/parlemtrack` sur le VPS), après le premier déploiement réel.

#### Corrigé
- Module `pipeline` absent de l'image Docker du backend (BUG-010).
- Droits d'écriture refusés sur `.next/cache` pour l'utilisateur non-root
  du frontend (BUG-011).
- Migrations Alembic non appliquées automatiquement en production (BUG-013).
- Cron de collecte tentant de joindre PostgreSQL/Redis directement depuis
  le runner GitHub, alors qu'ils ne sont pas exposés à Internet.

### Phase 4 — Frontend Next.js (2026-07-21 → 2026-07-22)

#### Ajouté
- Client HTTP typé vers l'API FastAPI (`frontend/src/lib/api.ts`).
- Composants d'affichage accessibles : position de vote icône + texte,
  badges (groupe, mandat terminé, statut scrutin, cohérence macro).
- Visualisations de vote segmentées par groupe et jauges de score.
- Carte scrutin et colonnes d'arguments pour/contre parfaitement symétriques.
- Navigation principale avec menu burger accessible au clavier (RGAA).
- Pages Next.js branchées sur l'API réelle : accueil, listes (scrutins,
  députés, groupes), fiches, recherche, rubrique "Comprendre".
- PWA installable : manifeste, icônes générées, service worker.
- Script Playwright de captures d'écran automatiques (`scripts/captures.mjs`).

### Phase 3 — Analyse IA (2026-07-22)

#### Ajouté
- Insertion des analyses IA en base, jamais mises à jour une fois générées.
- Construction du prompt système d'analyse neutre — durci en cours de
  route avec une interdiction explicite de citer des statistiques
  chiffrées non sourcées, après un premier essai jugé trop affirmatif.
- Client Mistral avec gestion du rate limit et parsing de la réponse JSON.
- Génération par lot des analyses manquantes, avec throttling entre appels.
- Orchestration de la génération IA automatique bornée dans le run pipeline.

#### Corrigé
- Rafale de 429 (rate limit) lors d'un lot de génération (BUG-009).

### Phase 2 — Backend API (2026-07-21)

#### Ajouté
- Infrastructure API : session de base de données, cache Redis, sécurité
  (headers OWASP, CORS, rate limiting).
- Schémas Pydantic de réponse pour tous les endpoints.
- Services métier avec cache Redis (scrutins, députés, groupes,
  recherche, actualités, health).
- Routes API avec rate limiting et gestion des erreurs 404/422.
- Invalidation du cache API en fin de run du pipeline.
- Couverture de tests des routes API (nominal, 404, 422).
- Services postgres et redis dans la CI pour les tests backend.

#### Corrigé
- Port Redis hôte remappé (conflit avec un service système local, BUG-007).
- Résolution des imports pytest divergente entre local et CI (BUG-008).

### Phase 1 — Pipeline de collecte (2026-07-20 → 2026-07-21)

#### Ajouté
- Schéma SQLAlchemy complet et migrations Alembic.
- Téléchargement des archives AN avec détection de changement
  ETag/Last-Modified (pas de retéléchargement inutile).
- Parsers scrutins/députés/organes gérant les pièges réels du format AN
  (champ objet/tableau, uid `{"#text":...}`, valeurs numériques en
  chaîne...).
- Upsert idempotent et bascule automatique du statut actif des députés
  remplacés en cours de législature.
- Intégration des flux RSS presse et des scores Datan.
- Orchestration du pipeline avec récupération des députés remplacés
  (source AMO30 de l'AN).

#### Corrigé
- `lien_an` construit avec l'uid au lieu du numéro de scrutin (BUG-006).

### Phase 0 — Socle du projet (2026-07-20)

#### Ajouté
- Structure initiale du dépôt, environnement virtuel et dépendances Python.
- Docker Compose PostgreSQL/Redis pour le développement local.
- Configuration applicative et logging communs.
- Initialisation Alembic.
- Pipeline CI minimal (lint + tests).

#### Corrigé
- `requests` absent de `requirements.txt` (BUG-001).
