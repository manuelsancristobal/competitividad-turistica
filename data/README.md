# Datos: Competitividad Turística

## Origen
- **Tipo de Cambio y Precios**:
  - BCCH (Banco Central de Chile) vía API.
  - FRED (Federal Reserve Economic Data).
  - World Bank Open Data.
  - INDEC (Argentina) para IPC histórico.
  - Yahoo Finance / Bluelytics (Dólar Blue Argentina).

## Estructura
- `raw/`: Datos locales estáticos (si aplica).
- `processed/`: 
  - `datos_consolidados.csv`: Serie temporal final de TCRB y métricas de competitividad.
  - `fuentes_datos.json`: Metadata de la última ejecución del pipeline.
- `external/`: Cache de peticiones API para optimizar tiempos de ejecución y evitar límites de tasa.

## Diccionario de Datos Clave
- `TCRB`: Tipo de Cambio Real Bilateral.
- `TCRB_BLUE`: TCRB ajustado por mercado informal (específico para Argentina).
- `IPC`: Índice de Precios al Consumidor.
