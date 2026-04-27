"""
Generador de assets para Competitividad Turística.
Ejecuta el pipeline de datos y asegura que los archivos de salida estén actualizados.
"""

import logging
from competitividad_turistica.data.pipeline import run_pipeline
from competitividad_turistica.config.settings import FECHA_INICIO, FECHA_FIN

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger("GenerateAssets")
    
    logger.info("Iniciando generación de datos consolidados...")
    df, sources = run_pipeline(FECHA_INICIO, FECHA_FIN)
    
    if df is not None:
        logger.info(f"Pipeline completado. {len(df)} registros procesados.")
    else:
        logger.error("Error al ejecutar el pipeline.")
        exit(1)

if __name__ == "__main__":
    main()
