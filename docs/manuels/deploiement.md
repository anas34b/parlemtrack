# Manuel de déploiement — ParlemTrack

Ce manuel décrit la mise en production sur un VPS OVHcloud, déployé via SSH
depuis GitHub Actions (`.github/workflows/deploy.yml`).

> **Prérequis non encore présents dans ce dépôt**, à créer avant tout
> déploiement réel : `Dockerfile` pour le backend, `Dockerfile` pour le
> frontend, et `docker-compose.prod.yml` orchestrant backend + frontend +
> PostgreSQL + Redis en production. `docker-compose.yml` à la racine ne
> contient aujourd'hui que les services PostgreSQL/Redis de développement
> local. Le workflow `deploy.yml` référence `docker-compose.prod.yml` sur
> le serveur : sans ce fichier, le déploiement échouera même avec des
> secrets correctement configurés.

## 1. Création du VPS

1. Commander un VPS OVHcloud (Debian ou Ubuntu LTS récent).
2. Se connecter en SSH avec l'utilisateur initial fourni par OVHcloud.
3. Créer un utilisateur dédié au déploiement (ex. `deploy`), avec accès
   `sudo` et **sans mot de passe activé pour SSH** (authentification par
   clé uniquement) :
   ```bash
   adduser deploy
   usermod -aG sudo deploy
   ```
4. Installer Docker et Docker Compose sur le VPS :
   ```bash
   curl -fsSL https://get.docker.com | sh
   usermod -aG docker deploy
   ```
5. Créer l'arborescence de déploiement attendue par `deploy.yml` :
   ```bash
   mkdir -p /opt/parlemtrack/staging /opt/parlemtrack/production
   git clone <url-du-depot> /opt/parlemtrack/staging
   git clone <url-du-depot> /opt/parlemtrack/production
   ```
6. Copier un fichier `.env` réel (jamais commité) dans chacun des deux
   répertoires, à partir de `.env.example`, avec les vraies valeurs de
   production (clé Mistral, mot de passe PostgreSQL, etc.).

## 2. Configuration DNS

1. Chez le registrar du nom de domaine, créer les enregistrements :
   - `A` (ou `AAAA`) pointant vers l'IP du VPS pour le domaine de production.
   - Un sous-domaine dédié pour le staging (ex. `staging.mondomaine.fr`).
2. Attendre la propagation DNS (vérifier avec `dig` ou `nslookup`).
3. Mettre en place un reverse proxy avec certificat HTTPS (ex. Caddy ou
   Nginx + Certbot) sur le VPS, pointant vers les ports exposés par
   `docker-compose.prod.yml` — HTTPS est obligatoire en production
   (règle CLAUDE.md).

## 3. Ajout des secrets GitHub

Dans le dépôt GitHub : **Settings → Secrets and variables → Actions**.

Créer deux environnements (**Settings → Environments**) : `staging` et
`production`, puis, pour chacun (ou en secrets de dépôt partagés si les
valeurs sont identiques) :

| Secret | Description |
|---|---|
| `OVH_HOST` | Adresse IP ou nom d'hôte du VPS |
| `OVH_USER` | Utilisateur SSH de déploiement (ex. `deploy`) |
| `OVH_SSH_KEY` | Clé privée SSH dédiée au déploiement (jamais réutiliser une clé personnelle) |
| `OVH_PORT` | Port SSH du VPS (souvent `22`) |

Pour `pipeline-collecte.yml`, ajouter également au dépôt (pas besoin
d'environnement séparé, ce workflow n'est pas lié à staging/production) :

| Secret | Description |
|---|---|
| `DATABASE_URL` | URL PostgreSQL de production |
| `MISTRAL_API_KEY` | Clé API Mistral La Plateforme |
| `REDIS_URL` | URL Redis de production |

La clé SSH se génère localement (jamais sur le VPS) :

```bash
ssh-keygen -t ed25519 -C "deploiement-parlemtrack" -f deploy_key
```

La clé publique (`deploy_key.pub`) va dans `~/.ssh/authorized_keys` de
l'utilisateur `deploy` sur le VPS ; la clé privée (`deploy_key`) va dans
le secret GitHub `OVH_SSH_KEY`, jamais ailleurs.

## 4. Premier déploiement manuel de vérification

Avant de laisser la CI déployer automatiquement, valider une première
fois à la main depuis le VPS :

```bash
ssh deploy@<ip-du-vps>
cd /opt/parlemtrack/staging
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
docker compose -f docker-compose.prod.yml ps
curl -f http://localhost:8000/api/health
```

Une fois ce déploiement manuel validé (API accessible, migrations
appliquées, frontend qui répond), déclencher le workflow `Déploiement`
depuis l'onglet Actions de GitHub (ou pousser sur `main`) pour vérifier
que le déploiement automatique staging reproduit le même résultat.

Pour la production, le déclenchement se fait par un tag de version :

```bash
git tag v1.0
git push origin v1.0
```

## 5. Vérifications post-déploiement

- `GET /api/health` répond `200` avec `base_de_donnees: true` et
  `redis: true`.
- Le frontend charge la page d'accueil et affiche des scrutins réels.
- Les logs du backend (`docker compose logs backend`) ne montrent aucune
  erreur au démarrage.
- Le certificat HTTPS est valide (pas d'avertissement navigateur).
