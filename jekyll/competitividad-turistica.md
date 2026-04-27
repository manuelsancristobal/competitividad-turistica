---
layout: project
title: "Competitividad Turística: Monitoreo del Tipo de Cambio Real Bilateral"
category: Economía y Finanzas
description: "Dashboard interactivo para el análisis del TCRB de Chile frente a 12 mercados clave, automatizando la ingesta de datos desde BCCh, Yahoo Finance, FRED e INDEC."
github_url: "https://github.com/manuelsancristobal/competitividad-turistica"
tech_stack:
  - Python
  - Streamlit
  - Pandas
  - Plotly
  - Pydantic
  - BCCh API
  - Yahoo Finance
  - FRED API
---

La competitividad de un destino turístico está fuertemente influenciada por el costo relativo de los bienes y servicios para los visitantes extranjeros. Este proyecto automatiza el cálculo y visualización del **Tipo de Cambio Real Bilateral (TCRB)** de Chile frente a sus 12 principales mercados emisores de turistas, permitiendo identificar periodos de encarecimiento o abaratamiento relativo del país.

El análisis utiliza un pipeline de datos robusto que integra múltiples fuentes internacionales para construir una serie mensual armonizada desde el año 2000.

## Dashboard Interactivo

El proyecto se materializa en una aplicación de **Streamlit** que permite explorar:
1. **Evolución del TCRB:** Series históricas normalizadas.
2. **Descomposición del Índice:** Identificación de si la competitividad varía por tipo de cambio nominal o por diferenciales de inflación.
3. **Análisis de Volatilidad:** Regímenes de estabilidad vs. incertidumbre cambiaria.
4. **Correlaciones:** Cómo se mueven las monedas de la región frente al peso chileno.

<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 20px;">
    <strong>Nota:</strong> El dashboard está diseñado para ejecutarse localmente o en un servidor Streamlit. Los datos se actualizan automáticamente mediante el pipeline integrado.
</div>

## Metodología

El TCRB se calcula siguiendo la metodología estándar:
$$TCRB = \frac{e \cdot P^*}{P}$$
Donde:
- $e$ es el tipo de cambio nominal (CLP por moneda extranjera).
- $P^*$ es el nivel de precios (IPC) del país extranjero.
- $P$ es el nivel de precios (IPC) de Chile.

### Fuentes de Datos y Pipeline
Para asegurar la continuidad de las series, implementé un sistema de **cascada (fallback)**:
- **Tasas de Cambio:** Banco Central de Chile → Yahoo Finance.
- **Inflación (IPC):** Banco Central de Chile → FRED (St. Louis Fed) → World Bank → INDEC (para Argentina).

El sistema maneja automáticamente casos complejos como el **Dólar Blue en Argentina**, permitiendo comparar la competitividad oficial versus la del mercado informal, un factor crítico para el flujo turístico terrestre en el Cono Sur.

## Implementación Técnica

- **Arquitectura de Micro-servicios:** El código está organizado en capas claras: `data` (extracción), `calc` (lógica de negocio), `viz` (gráficos) y `products` (interfaz de usuario).
- **Validación con Pydantic:** Uso de modelos de datos para asegurar que las series descargadas cumplan con los formatos y calidad requeridos.
- **Estandarización de Procesos:** El proyecto cuenta con un `Makefile` y un CLI `run.py` para facilitar la reproducción del análisis y el despliegue de resultados.

---
*Este proyecto forma parte de mi portafolio de análisis de datos económicos aplicados al sector turismo.*
