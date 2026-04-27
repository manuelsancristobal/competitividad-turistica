"""Global configuration and constants for competitividad-turistica project."""

import os
from datetime import datetime
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "viz" # O donde se guarden los graficos estaticos

# Jekyll paths
_jekyll_env = os.getenv("JEKYLL_REPO", str(PROJECT_ROOT.parent / "manuelsancristobal.github.io"))
JEKYLL_REPO = Path(_jekyll_env)
JEKYLL_BASE = JEKYLL_REPO / "proyectos" / "competitividad-turistica"
JEKYLL_ASSETS_DIR = JEKYLL_BASE / "assets"
JEKYLL_PROJECTS_DIR = JEKYLL_REPO / "_projects"
JEKYLL_PROJECT_MD = PROJECT_ROOT / "jekyll" / "competitividad-turistica.md"

class Settings(BaseSettings):
    """Pydantic Settings definition."""
    # Data date range
    FECHA_INICIO: str = Field(default="2000-01-01")
    FECHA_FIN: str = Field(default_factory=lambda: datetime.today().strftime("%Y-%m-%d"))

    # API retry parameters
    MAX_REINTENTOS: int = Field(default=3)
    PAUSA_REINTENTO: int = Field(default=2)

    # Competitividad turistica calculation
    BASE_INDEX: float = Field(default=100.0)
    BASE_YEAR: int = Field(default=2015)

    # Narrative thresholds
    SIGMA_THRESHOLD: float = Field(default=1.5)
    VARIATION_MODERATE: float = Field(default=5.0)
    VARIATION_NOTABLE: float = Field(default=10.0)
    VARIATION_EXTREME: float = Field(default=20.0)

    # Volatility settings
    VOLATILITY_ANNUALIZE: bool = Field(default=True)

    # API credentials
    BCCH_USER: str = Field(default="")
    BCCH_PASS: str = Field(default="")

    # Cache settings
    CACHE_MAX_AGE_DAYS: int = Field(default=7)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instancia global de settings
settings_app = Settings()

# Para retrocompatibilidad con las importaciones directas en otros módulos
FECHA_INICIO = settings_app.FECHA_INICIO
FECHA_FIN = settings_app.FECHA_FIN
MAX_REINTENTOS = settings_app.MAX_REINTENTOS
PAUSA_REINTENTO = settings_app.PAUSA_REINTENTO
BASE_INDEX = settings_app.BASE_INDEX
BASE_YEAR = settings_app.BASE_YEAR
SIGMA_THRESHOLD = settings_app.SIGMA_THRESHOLD
VARIATION_MODERATE = settings_app.VARIATION_MODERATE
VARIATION_NOTABLE = settings_app.VARIATION_NOTABLE
VARIATION_EXTREME = settings_app.VARIATION_EXTREME
VOLATILITY_ANNUALIZE = settings_app.VOLATILITY_ANNUALIZE
BCCH_USER = settings_app.BCCH_USER
BCCH_PASS = settings_app.BCCH_PASS
CACHE_MAX_AGE_DAYS = settings_app.CACHE_MAX_AGE_DAYS
LOG_LEVEL = settings_app.LOG_LEVEL
