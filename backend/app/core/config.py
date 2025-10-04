from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Celeste X"
    database_path: Path = Path("data") / "celestex.db"
    frontend_dist_path: Path = Path("frontend") / "dist"

    class Config:
        env_prefix = "CELESTEX_"


def get_settings() -> Settings:
    return Settings()
