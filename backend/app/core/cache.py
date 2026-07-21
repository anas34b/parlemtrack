"""Cache Redis générique pour les réponses API : lecture/écriture JSON avec TTL."""

import json
import logging

import redis

from backend.app.core.config import get_settings

logger = logging.getLogger("backend.core.cache")

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Retourne un client Redis partagé (connexion paresseuse, une seule fois)."""
    global _client
    if _client is None:
        _client = redis.from_url(get_settings().redis_url, decode_responses=True)
    return _client


def get_cache(cle: str) -> dict | list | None:
    """Lit une valeur JSON en cache, ou None si absente."""
    brut = get_redis().get(cle)
    if brut is None:
        return None
    logger.info("cache hit : %s", cle)
    return json.loads(brut)


def set_cache(cle: str, valeur: dict | list, ttl_s: int | None = None) -> None:
    """Écrit une valeur JSON en cache avec expiration."""
    ttl = ttl_s if ttl_s is not None else get_settings().cache_ttl_s
    get_redis().set(cle, json.dumps(valeur, ensure_ascii=False), ex=ttl)


def invalider_prefixe(prefixe: str) -> int:
    """Supprime toutes les clés de cache commençant par `prefixe`. Retourne le nombre supprimé."""
    client = get_redis()
    cles = list(client.scan_iter(match=f"{prefixe}*"))
    if not cles:
        return 0
    return client.delete(*cles)
