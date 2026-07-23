# Image de production du backend FastAPI. Multi-stage : les outils de build
# (compilateurs, pip cache) ne se retrouvent jamais dans l'image finale.

FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
# requirements.txt est la seule source de vérité des dépendances (aussi
# utilisée par la CI) ; on exclut ici les outils dev-only (tests, lint) de
# l'image de production, sans dupliquer le fichier.
RUN grep -vE '^(pytest|pytest-cov|coverage|ruff)==' requirements.txt > requirements.prod.txt \
    && pip install --no-cache-dir --prefix=/install -r requirements.prod.txt

FROM python:3.12-slim AS runtime

RUN groupadd --system parlemtrack && useradd --system --gid parlemtrack parlemtrack

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/ backend/
COPY pipeline/ pipeline/
COPY alembic/ alembic/
COPY alembic.ini .
RUN chmod +x backend/docker-entrypoint.sh

USER parlemtrack

EXPOSE 8000

ENTRYPOINT ["backend/docker-entrypoint.sh"]
