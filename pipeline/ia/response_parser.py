"""Parsing de la réponse JSON de Mistral, avec nettoyage des éventuels fences ```json."""

import json
import re

CLES_ATTENDUES = {
    "resume_factuel",
    "arguments_pour",
    "arguments_contre",
    "coherence_macro",
    "indicateurs_ref",
}
VALEURS_COHERENCE = {"aligne", "mitige", "contradictoire"}

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class ReponseIAInvalide(Exception):
    """Levée quand la réponse de Mistral n'est pas un JSON exploitable."""


def parse_reponse_ia(texte: str) -> dict:
    """Extrait le JSON de la réponse brute de Mistral, fences ```json éventuelles retirées."""
    nettoye = _FENCE_RE.sub("", texte.strip()).strip()
    try:
        donnees = json.loads(nettoye)
    except json.JSONDecodeError as exc:
        raise ReponseIAInvalide(f"JSON invalide : {exc}") from exc

    if not isinstance(donnees, dict) or not CLES_ATTENDUES.issubset(donnees.keys()):
        raise ReponseIAInvalide(f"clés manquantes, attendu {CLES_ATTENDUES}")
    if donnees["coherence_macro"] not in VALEURS_COHERENCE:
        raise ReponseIAInvalide(f"coherence_macro invalide : {donnees['coherence_macro']!r}")

    return donnees
