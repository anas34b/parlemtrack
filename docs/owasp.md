# OWASP Top 10 (2021) — mesures ParlemTrack

Preuve de la compétence éliminatoire **C2.2.3**. Chaque catégorie est
mise en regard d'une mesure réellement implémentée dans le code, ou
d'une justification explicite de non-applicabilité — jamais d'affirmation
générique.

## A01:2021 — Broken Access Control

**Non applicable en v1, par conception.** L'application ne comporte
aucun compte utilisateur, aucune authentification, aucune ressource
privée : toute l'API est en lecture seule et publique
(`app.add_middleware(CORSMiddleware, allow_methods=["GET"], ...)` dans
`backend/app/main.py`). Il n'existe donc aucun contrôle d'accès à
contourner — la surface d'attaque de cette catégorie est nulle par
réduction du périmètre, pas par un contrôle non testé. À revoir si une
future version introduit des comptes (ex. modération, favoris).

## A02:2021 — Cryptographic Failures

Aucune donnée personnelle sensible n'est stockée (les données
parlementaires traitées sont déjà publiques via l'open data de l'AN).
Les seuls secrets du système (clé API Mistral, mot de passe PostgreSQL)
vivent exclusivement en variables d'environnement : `.env` est exclu du
dépôt (`.gitignore`), `.env.example` ne contient que des valeurs
factices, et en production ces valeurs sont injectées via le `.env` du
serveur (`docker-compose.prod.yml`), jamais dans un secret GitHub ni un
commit (voir `docs/manuels/mise-a-jour.md` §4).

**Limite connue** : le VPS de démonstration actuel
(`91.134.88.221:3000`) sert en HTTP simple, sans certificat TLS — le
reverse proxy HTTPS documenté dans `docs/manuels/deploiement.md` §2
n'a pas encore été mis en place. Correction prévue en v1.1.

## A03:2021 — Injection

- **SQL** : toutes les requêtes passent par SQLAlchemy (ORM et Core,
  `select`/`insert().on_conflict_do_update`), aucune requête SQL n'est
  concaténée en chaîne de caractères nulle part dans le code (vérifié :
  aucune occurrence de `execute(f"..."` ou équivalent dans `backend/`
  ni `pipeline/`). La recherche (`backend/app/services/recherche_service.py`)
  utilise `Scrutin.titre.ilike(f"%{q}%")` — le motif est interpolé côté
  Python mais transmis en paramètre lié à psycopg2, jamais dans le SQL
  littéral : un `q` du type `' OR '1'='1` est traité comme une sous-chaîne
  littérale à chercher, pas comme du SQL (cas de recette SEC01).
- **Entrées** : chaque paramètre d'entrée de l'API est typé et validé
  par Pydantic/FastAPI (`Query`, `Path`, schémas de requête), avant
  d'atteindre la couche métier.
- Aucun `eval`, `exec`, ni désérialisation dangereuse : tout le
  parsing de données externes (archives AN, réponses Mistral, cache
  Redis) passe par `json.loads`, jamais `pickle` ni `yaml.load`.

## A04:2021 — Insecure Design

- **Limitation de débit** (`slowapi`, `RATE_LIMIT` par défaut
  `60/minute`) sur chaque route, pour limiter l'abus et le scraping
  massif.
- **Analyses IA immuables** : `inserer_analyse_ia()`
  (`pipeline/store/upsert.py`) utilise `ON CONFLICT DO NOTHING` — une
  analyse déjà générée ne peut jamais être écrasée par un rejeu du
  pipeline, ce qui empêche une exécution compromise de falsifier une
  analyse déjà publiée.
- **CORS restreint** à une liste explicite d'origines (`CORS_ORIGINS`),
  pas de wildcard `*`.

## A05:2021 — Security Misconfiguration

- Middleware d'en-têtes de sécurité (`HeadersSecuriteMiddleware`) sur
  chaque réponse : `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`,
  `Permissions-Policy: geolocation=(), microphone=(), camera=()`.
- En production, PostgreSQL, Redis et le backend ne sont **pas**
  exposés sur l'hôte (`docker-compose.prod.yml`, réseau Docker interne
  uniquement) — seul le frontend publie un port.
- Les conteneurs backend et frontend tournent en **utilisateur
  non-root** (`backend/Dockerfile`, `frontend/Dockerfile`).
- **Limite acceptée** : la documentation interactive FastAPI
  (`/docs`, `/openapi.json`) reste activée par défaut (aucun
  `docs_url=None` défini dans `backend/app/main.py`) — accepté car
  l'API est publique et en lecture seule, sans secret exposé dans le
  schéma ; à durcir si l'API devient plus sensible.
- **Limite acceptée** : les images de base des `Dockerfile`
  (`python:3.12-slim`, `node:22-alpine`) sont épinglées par tag, pas
  par hash SHA — Dependabot (écosystème `github-actions` et `pip`)
  couvre les mises à jour de version mais pas un pin par digest.

## A06:2021 — Vulnerable and Outdated Components

`requirements.txt` est intégralement épinglé en versions exactes
(`==`). `.github/dependabot.yml` surveille chaque semaine quatre
écosystèmes (`pip` racine, `npm` frontend, `npm` scripts,
`github-actions`) et ouvre une pull request par dépendance obsolète,
qui passe automatiquement par la CI avant fusion (voir
`docs/manuels/mise-a-jour.md` §1).

## A07:2021 — Identification and Authentication Failures

**Non applicable en v1, par conception** — même constat qu'A01 : aucun
mécanisme d'authentification (pas de mot de passe, pas de session, pas
de JWT) n'existe dans le code (`grep` sur `backend/app` : aucune
occurrence de `login`, `password`, `jwt`, `session`, `cookie`). Rien à
casser tant qu'aucun compte n'existe.

## A08:2021 — Software and Data Integrity Failures

- La CI (`ci.yml`) exécute lint + tests backend et frontend sur
  **chaque pull request**, y compris celles ouvertes automatiquement
  par Dependabot — aucune dépendance n'est mise à jour sans passer par
  cette vérification.
- Aucune désérialisation non sûre (voir A03) : pas de `pickle`, pas de
  chargement de code exécutable depuis une source externe.
- Les migrations Alembic sont versionnées et relues avant merge (voir
  `docs/manuels/mise-a-jour.md` §3) ; elles s'appliquent automatiquement
  et de façon identique à chaque déploiement
  (`backend/docker-entrypoint.sh`), pas de modification manuelle du
  schéma en production.

## A09:2021 — Security Logging and Monitoring Failures

- Logging structuré et horodaté dans tout le projet
  (`backend/app/core/logging.py`), niveaux utilisés correctement
  (WARNING sur les échecs gérés, ERROR sur les échecs bloquants).
- Chaque run du pipeline est enregistré en base
  (table `collectes_log` : nombre de scrutins traités, d'erreurs,
  durée, statut).
- Un échec du cron de collecte nocturne ouvre automatiquement une
  issue GitHub de suivi (`pipeline-collecte.yml`).
- **Limite acceptée** : pas de solution de supervision/alerting
  centralisée (SIEM, Sentry...) au-delà des logs et de l'issue
  GitHub — proportionné à l'échelle actuelle du projet, à revoir en
  cas de montée en charge réelle.

## A10:2021 — Server-Side Request Forgery (SSRF)

**Non applicable.** Tous les appels HTTP sortants (téléchargement AN,
API Datan, flux RSS, API Mistral) ciblent des URLs **constantes,
codées en dur** dans le code (`pipeline/collect/downloader.py`,
`pipeline/collect/datan.py`, `pipeline/collect/rss_presse.py`) —
aucune route de l'API ne construit une requête sortante à partir d'une
entrée utilisateur. Il n'existe donc aucun point d'entrée SSRF.
