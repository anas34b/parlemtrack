"""Configuration commune du module logging, utilisée par tout le projet."""

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure le logging racine avec un format horodaté unique."""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger nommé, prêt à l'emploi."""
    return logging.getLogger(name)
