# Competitividad Turística - Análisis de TCRB Multimercado

## Impacto y Valor del Proyecto
Este proyecto calcula el Índice de Competitividad Turística de Chile mediante el Tipo de Cambio Real Bilateral (TCRB) ajustado por inflación, permitiendo monitorear qué tan costoso es Chile para sus principales mercados emisores (Argentina, Brasil, USA, Europa). Incluye un ajuste pionero por el "Dólar Blue" argentino para capturar la competitividad real en contextos de brecha cambiaria. Es una herramienta esencial para la planificación de campañas de promoción internacional basadas en poder adquisitivo relativo.

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
