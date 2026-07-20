"""Configuration de l'application, chargée depuis les variables d'environnement."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres globaux de ParlemTrack, lus depuis `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str
    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"
    env: str = "dev"


@lru_cache
def get_settings() -> Settings:
    """Retourne les paramètres, mis en cache pour éviter de relire `.env`."""
    return Settings()
