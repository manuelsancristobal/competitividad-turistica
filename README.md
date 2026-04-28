# Competitividad Turística - Análisis de TCRB Multimercado

## Contexto
Este proyecto nació de un correo electrónico que en 2021 le mandé a un profesor de mi posgrado, en él le aseguraba que veía una caída del Real Brasileño respecto al Peso Chileno, por lo que podía interpretar que era un desincentivo a la visita de los brasileños. Me respondió, de manera cortés, que no sabía qué cifras estaba mirando, porque la realidad (de 2021) era una depreciación del Peso ante el Real, lo que hacía conveniente visitar Chile. En esta confusión, y después de leer y no entender nada sobre los Tipo de Cambio Real Bilateral (TCRB), en 2026 decidí hacer este dashboard para aclarármelo de una vez por todas.

## Impacto y Valor del Proyecto
Este proyecto calcula un Índice de Competitividad Turística de Chile mediante el TCRB ajustado por inflación, permitiendo monitorear qué tan costoso es Chile para sus principales mercados emisores (Argentina, Brasil, USA, Europa). También incluye un ajuste con el "Dólar Blue" argentino para capturar la competitividad real en contextos de brecha cambiaria. Con esto, puedes hacer una planificación de campañas de promoción internacional basadas en el poder adquisitivo relativo.

## Stack Tecnológico
- **Lenguaje**: Python 3.10+
- **Librerías Clave**: `Pandas`, `Pydantic` (Validación), `Plotly` (Dashboard), `Requests`.
- **Calidad de Código**: `Ruff`, `Pytest`, `Pre-commit`.
- **Infraestructura**: Docker, GitHub Actions.

## Arquitectura de Datos y Metodología
1. **Ingesta Multinivel**: Conectores para APIs del Banco Central de Chile, FRED, Banco Mundial y Yahoo Finance.
2. **Normalización**: Alineación de series temporales de IPC y tipos de cambio con diferentes periodicidades.
3. **Cálculo de TCRB**: Aplicación de fórmulas de paridad de poder adquisitivo para generar índices de competitividad.
4. **Análisis Estadístico**: Detección de estacionalidad, volatilidad cambiaria y correlación multimercado.
5. **Dashboard**: Interfaz interactiva para la visualización de series históricas y métricas de riesgo.

## Quick Start (Reproducibilidad)
1. `git clone https://github.com/manuelsancristobal/competitividad-turistica`
2. `make install-dev`
3. `make test`
4. `make run` (Ejecuta el pipeline completo de actualización de datos)
5. `make dashboard` (Inicia el dashboard interactivo en `localhost:8050`)

## Estructura del Proyecto
- `src/`: Lógica de cálculo, conectores de datos y visualización.
- `data/`: Cache de APIs y resultados procesados (`external/`, `processed/`).
- `docs/`: Documentación técnica y metodológica detallada.

---
**Autor**: Manuel San Cristóbal Opazo  
**Licencia**: MIT
