# Image de production du frontend Next.js, via le mode "standalone"
# (voir next.config.ts) : seuls les fichiers réellement nécessaires au
# runtime sont copiés, pas node_modules complet ni le code source.

FROM node:22-alpine AS deps

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

# Aucun appel réseau au backend n'est nécessaire au build : toutes les pages
# qui dépendent de l'API sont rendues à la demande (dynamic), jamais au
# moment du build (vérifié en local avec un API_URL injoignable).
RUN npm run build

FROM node:22-alpine AS runtime

RUN addgroup --system parlemtrack && adduser --system --ingroup parlemtrack parlemtrack

WORKDIR /app

# --chown : le serveur Next tourne en utilisateur non-root et doit pouvoir
# écrire dans .next/cache (cache de rendu incrémental) au runtime.
COPY --from=builder --chown=parlemtrack:parlemtrack /app/.next/standalone ./
COPY --from=builder --chown=parlemtrack:parlemtrack /app/.next/static ./.next/static
COPY --from=builder --chown=parlemtrack:parlemtrack /app/public ./public
RUN mkdir -p .next/cache && chown parlemtrack:parlemtrack .next/cache

USER parlemtrack

ENV PORT=3000
EXPOSE 3000

CMD ["node", "server.js"]
