from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Pi-hole database paths
    ftl_db_path: str = "/etc/pihole/pihole-FTL.db"
    gravity_db_path: str = "/etc/pihole/gravity.db"

    # App-owned database
    dashboard_db_path: str = str(
        Path(__file__).resolve().parent.parent / "dashboard.db"
    )

    # Pi-hole CLI
    pihole_command: str = "pihole"
    use_sudo: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Frontend static files
    static_dir: str = str(
        Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    )

    # Cache TTLs (seconds)
    stats_cache_ttl: int = 10
    heavy_cache_ttl: int = 60

    model_config = {"env_prefix": "PIHOLE_DASH_"}


settings = Settings()
