# Manuel de mise à jour — ParlemTrack

## 1. Mise à jour des dépendances (Dependabot)

Dependabot est configuré via `.github/dependabot.yml` sur quatre
écosystèmes, chacun vérifié une fois par semaine :

| Écosystème | Répertoire | Couvre |
|---|---|---|
| `pip` | `/` | `requirements.txt` (backend + pipeline) |
| `npm` | `/frontend` | dépendances Next.js/React/Jest |
| `npm` | `/scripts` | Playwright (captures d'écran) |
| `github-actions` | `/` | versions des actions utilisées dans `.github/workflows/*.yml` |

Dependabot ouvre une pull request par dépendance obsolète (jusqu'à 10
en parallèle pour pip/frontend, 5 pour scripts). Chaque PR déclenche
automatiquement la CI (`ci.yml`, sur `pull_request`) : lint + tests
backend + lint/test/build frontend. Processus de revue :

1. Vérifier que la CI est verte sur la PR.
2. Pour une montée de version majeure (change de premier chiffre, ex.
   `fastapi 0.x → 1.x`), lire le changelog de la dépendance avant de
   merger — la CI verte ne garantit pas l'absence de changement de
   comportement non couvert par les tests.
3. Merger via l'interface GitHub (pas de commande locale nécessaire).
4. Redéployer si le changement concerne une dépendance de production
   (`git push` sur `main` suffit, `deploy.yml` s'en charge).

Les alertes de sécurité Dependabot (vulnérabilités connues, distinctes
des mises à jour de version) sont visibles dans l'onglet **Security**
du dépôt GitHub et ne nécessitent pas de configuration supplémentaire.

## 2. Montée de version (tags git)

Les tags (`v0.1`, `v1.0`...) marquent des jalons de version, mais ne
déclenchent **pas** de déploiement automatique — `deploy.yml` ne se
déclenche que sur push vers `main` (un seul environnement de
déploiement, voir `docs/manuels/deploiement.md`). Un tag documente une
version livrée, il n'agit pas sur l'infrastructure :

```bash
git tag -a v1.0 -m "Version 1.0 — rendu de certification"
git push origin v1.0
```

Ajouter l'entrée correspondante dans `CHANGELOG.md` avant de tagger.

## 3. Migrations Alembic

Après toute modification d'un modèle SQLAlchemy (`backend/app/models/`) :

```bash
source .venv/bin/activate
alembic revision --autogenerate -m "description courte de la migration"
```

1. **Toujours relire le fichier généré** dans `alembic/versions/` — la
   génération automatique peut manquer des cas (renommage de colonne
   perçu comme suppression + ajout, contraintes complexes...).
2. Tester la migration en local sur la base de dev :
   ```bash
   alembic upgrade head
   ```
3. Vérifier `alembic downgrade -1` puis `alembic upgrade head` à
   nouveau, pour confirmer que la migration est réversible sans perte
   de structure inattendue.
4. Committer le fichier de migration avec le code qui en dépend, dans
   le même commit (pas de migration orpheline).

En production, les migrations s'appliquent **automatiquement** au
démarrage du conteneur `backend` (`backend/docker-entrypoint.sh`,
voir BUG-013) : un `git push` sur `main` suivi du redéploiement suffit,
aucune commande manuelle n'est nécessaire sur le VPS.

## 4. Rotation de la clé API Mistral

1. Générer une nouvelle clé sur [La Plateforme Mistral](https://console.mistral.ai/)
   (sans révoquer l'ancienne immédiatement, pour éviter une coupure).
2. Mettre à jour la valeur sur le VPS, dans `~/parlemtrack/.env`
   (jamais dans un commit, jamais dans un secret GitHub — cette clé
   n'est utilisée que côté serveur, par le conteneur `backend`) :
   ```bash
   ssh <utilisateur>@<ip-du-vps>
   cd ~/parlemtrack
   nano .env   # remplacer MISTRAL_API_KEY
   docker compose -f docker-compose.prod.yml up -d backend
   ```
3. Vérifier qu'une analyse se génère bien avec la nouvelle clé (`docker
   compose exec backend python -c "..."` ou attendre le prochain run du
   cron `pipeline-collecte.yml`).
4. Révoquer l'ancienne clé sur La Plateforme Mistral une fois la
   nouvelle confirmée fonctionnelle.
