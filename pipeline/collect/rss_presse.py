"""Lecture des flux RSS presse (actualité politique) via feedparser."""

import logging

import feedparser

logger = logging.getLogger("pipeline.collect.rss_presse")

FLUX_PRESSE = {
    "Le Monde": "https://www.lemonde.fr/politique/rss_full.xml",
    "Le Figaro": "https://www.lefigaro.fr/rss/figaro_politique.xml",
    "France Info": "https://www.franceinfo.fr/politique.rss",
}


def parse_entree(entree: dict, source: str) -> dict:
    """Normalise une entrée de flux RSS en dict prêt à stocker."""
    return {
        "source": source,
        "titre": entree.get("title", ""),
        "lien": entree.get("link", ""),
        "date_publication": entree.get("published", ""),
    }


def recuperer_actualites(nb_max_par_flux: int = 10) -> list[dict]:
    """Récupère les derniers titres des flux presse configurés.

    Un flux en échec (réseau, format invalide) est loggé en WARNING et
    n'interrompt pas la récupération des autres flux.
    """
    actualites = []
    for source, url in FLUX_PRESSE.items():
        flux = feedparser.parse(url)
        if flux.bozo:
            logger.warning("flux RSS %s illisible : %s", source, flux.bozo_exception)
            continue
        for entree in flux.entries[:nb_max_par_flux]:
            actualites.append(parse_entree(entree, source))
        logger.info("flux %s : %d titres récupérés", source, len(flux.entries[:nb_max_par_flux]))
    return actualites
