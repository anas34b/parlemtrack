# Manuel de déploiement — ParlemTrack

Ce manuel décrit la mise en production sur un VPS OVHcloud, déployé via SSH
depuis GitHub Actions (`.github/workflows/deploy.yml`).

`backend/Dockerfile`, `frontend/Dockerfile` et `docker-compose.prod.yml`
(backend, frontend, PostgreSQL, Redis) existent dans le dépôt et ont été
testés en réel en local : `docker compose -f docker-compose.prod.yml up
--build` démarre les 4 services, l'API répond sur `/api/health` et le
frontend sert des pages réelles (`/`, `/scrutins`, `/deputes`, `/groupes`,
`/comprendre`) après application des migrations (`alembic upgrade head`).
Seul le frontend publie un port sur l'hôte ; PostgreSQL, Redis et le
backend ne sont joignables que depuis le réseau Docker interne — voir
la section 6 pour le détail des images.

> **Ce que ce test local ne couvre pas** : le VPS OVHcloud réel, le DNS,
> le reverse proxy HTTPS et les secrets GitHub (`OVH_HOST`, `OVH_SSH_KEY`,
> etc.) ne peuvent être vérifiés que sur l'infrastructure réelle — suivre
> les sections 1 à 5 pour la première mise en production effective.

Un seul environnement de déploiement est utilisé ici (pas de distinction
staging/production séparée) : un clone unique sur le VPS, redéployé à
chaque push sur `main`.

## 1. Création du VPS

1. Commander un VPS OVHcloud (Debian ou Ubuntu LTS récent).
2. Se connecter en SSH avec l'utilisateur fourni par OVHcloud (souvent
   `ubuntu` sur une image Ubuntu — utilisable tel quel comme utilisateur
   de déploiement, un utilisateur `deploy` dédié n'est pas obligatoire
   pour un projet de cette taille).
3. Installer Docker et le plugin Docker Compose sur le VPS :
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```
   (se déconnecter/reconnecter pour que l'appartenance au groupe `docker`
   prenne effet).
4. Cloner le dépôt dans le répertoire personnel de l'utilisateur SSH,
   chemin attendu par `deploy.yml` et `pipeline-collecte.yml` :
   ```bash
   git clone <url-du-depot> ~/parlemtrack
   ```
5. Copier un fichier `.env` réel (jamais commité) à la racine de
   `~/parlemtrack`, à partir de `.env.example`, avec les vraies valeurs
   de production (clé Mistral, mot de passe PostgreSQL, etc.).

## 2. Configuration DNS

1. Chez le registrar du nom de domaine, créer un enregistrement `A` (ou
   `AAAA`) pointant vers l'IP du VPS.
2. Attendre la propagation DNS (vérifier avec `dig` ou `nslookup`).
3. Mettre en place un reverse proxy avec certificat HTTPS (ex. Caddy ou
   Nginx + Certbot) sur le VPS, pointant vers le port publié par
   `docker-compose.prod.yml` — HTTPS est obligatoire en production
   (règle CLAUDE.md).

## 3. Ajout des secrets GitHub

Dans le dépôt GitHub : **Settings → Secrets and variables → Actions**,
en secrets de dépôt (pas besoin d'environnements GitHub séparés avec un
seul environnement de déploiement) :

| Secret | Description |
|---|---|
| `OVH_HOST` | Adresse IP ou nom d'hôte du VPS |
| `OVH_USER` | Utilisateur SSH (ex. `ubuntu`) |
| `OVH_SSH_KEY` | Clé privée SSH dédiée au déploiement (jamais réutiliser une clé personnelle) |
| `OVH_PORT` | Port SSH du VPS (souvent `22`) |

`pipeline-collecte.yml` (le cron nocturne) réutilise ces mêmes secrets
`OVH_*` : il n'a pas de secrets qui lui sont propres. PostgreSQL et Redis
ne sont volontairement pas exposés sur l'hôte (voir
`docker-compose.prod.yml`), donc le cron ne s'y connecte pas directement
depuis le runner GitHub — il se connecte en SSH au VPS et exécute
`python -m pipeline.run` **à l'intérieur** du conteneur `backend` déjà en
cours d'exécution (`docker compose exec`), qui a déjà accès à
`DATABASE_URL`/`MISTRAL_API_KEY`/`REDIS_URL` via le `.env` du serveur.
Ces valeurs n'ont donc besoin d'être définies qu'une seule fois, sur le
VPS — jamais dans les secrets GitHub.

La clé SSH se génère localement (jamais sur le VPS) :

```bash
ssh-keygen -t ed25519 -C "deploiement-parlemtrack" -f deploy_key
```

La clé publique (`deploy_key.pub`) va dans `~/.ssh/authorized_keys` de
l'utilisateur SSH sur le VPS ; la clé privée (`deploy_key`) va dans le
secret GitHub `OVH_SSH_KEY`, jamais ailleurs.

## 4. Premier déploiement manuel de vérification

Avant de laisser la CI déployer automatiquement, valider une première
fois à la main depuis le VPS :

```bash
ssh <utilisateur>@<ip-du-vps>
cd ~/parlemtrack
docker compose -f docker-compose.prod.yml up -d --build
# Les migrations s'appliquent automatiquement au démarrage du conteneur
# backend (backend/docker-entrypoint.sh) — pas de commande séparée à lancer.
docker compose -f docker-compose.prod.yml ps

# Le backend n'expose aucun port sur l'hôte (réseau interne uniquement) et
# l'image ne contient pas curl : vérifier /api/health avec httpx (déjà une
# dépendance du projet), depuis l'intérieur du conteneur.
docker compose -f docker-compose.prod.yml exec -T backend python3 -c \
  "import httpx; print(httpx.get('http://localhost:8000/api/health').json())"

# Le frontend, lui, publie un port sur l'hôte (FRONTEND_PORT, 3000 par défaut).
curl -f http://localhost:3000/
```

Une fois ce déploiement manuel validé (API accessible, migrations
appliquées, frontend qui répond), déclencher le workflow `Déploiement`
depuis l'onglet Actions de GitHub (ou pousser sur `main`) pour vérifier
que le déploiement automatique reproduit le même résultat.

## 5. Vérifications post-déploiement

- `GET /api/health` répond `200` avec `base_de_donnees: true` et
  `redis: true`.
- Le frontend charge la page d'accueil et affiche des scrutins réels.
- Les logs du backend (`docker compose logs backend`) ne montrent aucune
  erreur au démarrage.
- Le certificat HTTPS est valide (pas d'avertissement navigateur).

## 6. Les images de production

- **`backend/Dockerfile`** : multi-stage `python:3.12-slim`. Le stage
  `builder` installe les dépendances de `requirements.txt` dans un
  préfixe isolé, en excluant les outils dev-only (`pytest`, `ruff`,
  `coverage`) — inutiles et non désirés en production. Le stage
  `runtime` copie uniquement ce préfixe + le code (`backend/`,
  `pipeline/` — utilisé en interne par certains services backend —,
  `alembic/`), tourne en utilisateur non-root. **≈ 208 Mo.**
- **`frontend/Dockerfile`** : multi-stage `node:22-alpine`, s'appuie sur
  le mode `output: "standalone"` de Next.js (`next.config.ts`), qui ne
  trace et ne copie que les fichiers réellement nécessaires au runtime —
  pas de `node_modules` complet, pas de code source. Tourne en
  utilisateur non-root ; attention à bien `--chown` les fichiers copiés
  et créer `.next/cache` avec les bons droits, sinon le serveur Next
  échoue silencieusement à écrire son cache de rendu (bug rencontré et
  corrigé lors du test local, voir ci-dessous). **≈ 218 Mo.**
- Aucune de ces deux images ne fait d'appel réseau à l'API pendant le
  `build` : toutes les pages qui dépendent du backend sont rendues à la
  demande (`dynamic`), jamais générées statiquement au moment du build.
  C'est ce qui permet au job `frontend` de la CI de construire l'image
  sans base de données ni backend actifs.

### Résultat du test réel effectué en local

`docker compose -f docker-compose.prod.yml up --build` a été exécuté en
conditions réelles (build complet des deux images, démarrage des 4
services, `alembic upgrade head` sur une base neuve) :

| Vérification | Résultat |
|---|---|
| `postgres` et `redis` démarrent, healthchecks au vert | OK |
| `backend` démarre et se connecte à PostgreSQL/Redis | OK |
| `GET /api/health` (depuis le réseau interne) | `200`, `base_de_donnees: true`, `redis: true` |
| `frontend` démarre (image standalone) | OK |
| `/`, `/scrutins`, `/deputes`, `/groupes`, `/comprendre` (port publié) | `200` |

Un bug réel a été trouvé et corrigé pendant ce test : le serveur Next
tournant en utilisateur non-root n'avait pas les droits d'écriture sur
`.next/cache` (répertoire resté possédé par `root` après le `COPY`
depuis le stage de build), ce qui faisait échouer silencieusement le
cache de rendu incrémental sur les pages dynamiques. Corrigé avec
`COPY --chown` et une création explicite de `.next/cache` avec les bons
droits avant de basculer sur l'utilisateur non-root.

Ce test a été fait avec une base de données neuve (schéma migré, aucune
donnée) et une clé Mistral factice — il valide l'orchestration Docker,
pas les données ni les appels IA réels.
