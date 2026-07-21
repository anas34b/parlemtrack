# ParlemTrack — frontend

Interface citoyenne Next.js 14+ (App Router, TypeScript, PWA), branchée sur
l'API FastAPI du dépôt (`../backend`).

## Installation

```bash
npm install
cp .env.example .env.local   # API_URL par défaut : http://localhost:8000
```

## Lancement

```bash
npm run dev     # serveur de développement (http://localhost:3000)
npm run build   # build de production
npm run start   # sert le build de production
```

L'API FastAPI (`uvicorn backend.app.main:app`) et les services Docker
(`docker compose up -d` à la racine du dépôt) doivent tourner en parallèle.

## Commandes utiles

```bash
npm run lint    # ESLint
npm run test    # Jest + Testing Library
npm run build   # build + vérification TypeScript
```

## Structure

```
src/app/          pages (App Router) : accueil, scrutins, deputes, groupes,
                   recherche, comprendre (rubrique pédagogique), PWA (manifest, icônes)
src/components/    composants réutilisables (CarteScrutin, PositionVote, ...)
src/lib/api.ts     client HTTP vers l'API FastAPI réelle
src/types/api.ts   types miroir des schémas Pydantic du backend
public/sw.js       service worker (PWA, cache réseau-d'abord)
```

Documentation complète du projet : voir [../docs/](../docs/).
