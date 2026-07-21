"""Client Mistral La Plateforme : appel, retries avec backoff, comptage des tokens."""

import logging
import time

from mistralai.client import Mistral

from backend.app.core.config import Settings, get_settings
from pipeline.ia.prompt_builder import PROMPT_SYSTEME, build_user_prompt
from pipeline.ia.response_parser import parse_reponse_ia

logger = logging.getLogger("pipeline.ia.mistral_client")

TIMEOUT_MS = 30_000
NB_RETRIES = 2
BACKOFF_S = 2.0
BACKOFF_RATE_LIMIT_S = 15.0


def _est_rate_limit(exc: Exception) -> bool:
    """Détecte une erreur 429 (rate limit) de l'API Mistral, qui exige un backoff plus long."""
    return getattr(getattr(exc, "raw_response", None), "status_code", None) == 429


def generer_analyse(scrutin: dict, settings: Settings | None = None) -> dict:
    """Appelle Mistral pour analyser un scrutin.

    Retourne un dict `analyse_ia` complet (données parsées + modele_utilise +
    tokens_utilises), prêt pour le stockage. Deux retries avec backoff
    linéaire en cas d'échec réseau ou d'erreur API.
    """
    settings = settings or get_settings()
    client = Mistral(api_key=settings.mistral_api_key)
    messages = [
        {"role": "system", "content": PROMPT_SYSTEME},
        {"role": "user", "content": build_user_prompt(scrutin)},
    ]

    derniere_erreur: Exception | None = None
    for tentative in range(NB_RETRIES + 1):
        try:
            reponse = client.chat.complete(
                model=settings.mistral_model,
                messages=messages,
                response_format={"type": "json_object"},
                timeout_ms=TIMEOUT_MS,
            )
            break
        except Exception as exc:  # réseau, timeout, erreur API Mistral
            derniere_erreur = exc
            logger.warning(
                "appel Mistral échoué pour %s (tentative %d/%d) : %s",
                scrutin.get("uid"),
                tentative + 1,
                NB_RETRIES + 1,
                exc,
            )
            if tentative < NB_RETRIES:
                attente = BACKOFF_RATE_LIMIT_S if _est_rate_limit(exc) else BACKOFF_S * (tentative + 1)
                time.sleep(attente)
    else:
        raise derniere_erreur

    donnees = parse_reponse_ia(reponse.choices[0].message.content)
    tokens = reponse.usage.total_tokens if reponse.usage else 0

    return {
        **donnees,
        "modele_utilise": settings.mistral_model,
        "tokens_utilises": tokens,
    }
