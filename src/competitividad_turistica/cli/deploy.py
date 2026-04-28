"""Copia assets y markdown del proyecto competitividad-turistica al repo Jekyll local."""

import logging
import shutil

from competitividad_turistica.config.settings import (
    JEKYLL_ASSETS_DIR,
    JEKYLL_PROJECT_MD,
    JEKYLL_PROJECTS_DIR,
    JEKYLL_REPO,
    OUTPUT_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def deploy() -> None:
    """Copia el archivo markdown y datos relevantes al repo Jekyll."""
    if not JEKYLL_REPO.exists():
        logger.error(f"Repositorio Jekyll no encontrado en {JEKYLL_REPO}")
        return

    # 1. Preparar directorios
    logger.info(f"Usando repo Jekyll en: {JEKYLL_REPO}")
    JEKYLL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    JEKYLL_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Copiar archivos de datos (opcional, para visualización estática si se requiere)
    if OUTPUT_DIR.exists():
        logger.info("Copiando datos consolidados a assets de Jekyll...")
        for data_file in OUTPUT_DIR.glob("*"):
            if data_file.is_file():
                shutil.copy2(data_file, JEKYLL_ASSETS_DIR / data_file.name)

    # 3. Copiar archivo Markdown del proyecto
    logger.info("Copiando archivo markdown...")
    if JEKYLL_PROJECT_MD.exists():
        shutil.copy2(JEKYLL_PROJECT_MD, JEKYLL_PROJECTS_DIR / "competitividad-turistica.md")
        logger.info("Despliegue local completado exitosamente.")
    else:
        logger.warning(f"No se encontró el archivo markdown en {JEKYLL_PROJECT_MD}")


if __name__ == "__main__":
    deploy()
