"""Cache Redis des dernières actualités presse (pas de table dédiée, TTL court)."""

import json

import redis

CLE_REDIS = "actualites:presse"
TTL_S = 6 * 3600


def enregistrer_actualites(client: redis.Redis, actualites: list[dict]) -> None:
    """Stocke la liste des actualités en JSON dans Redis, avec expiration."""
    client.set(CLE_REDIS, json.dumps(actualites, ensure_ascii=False), ex=TTL_S)


def lire_actualites(client: redis.Redis) -> list[dict]:
    """Relit les actualités en cache, liste vide si rien n'est encore stocké."""
    brut = client.get(CLE_REDIS)
    if brut is None:
        return []
    return json.loads(brut)
