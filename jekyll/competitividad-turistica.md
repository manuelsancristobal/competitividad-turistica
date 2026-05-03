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

**El costo relativo de los bienes y servicios para visitantes extranjeros determina la competitividad de un destino turístico.** Este proyecto automatiza el cálculo y la visualización del **Tipo de Cambio Real Bilateral (TCRB)** de Chile frente a sus 12 principales mercados emisores. La herramienta permite identificar periodos de encarecimiento o abaratamiento relativo del país de forma directa.

## Capacidades del Dashboard de Streamlit

Como se aprecia en la aplicación interactiva, el sistema permite realizar un monitoreo exhaustivo de:
1. **Evolución del TCRB:** Series históricas con normalización para facilitar la comparativa.
2. **Descomposición del Índice:** Análisis de si la competitividad varía por el tipo de cambio nominal o por diferenciales de inflación.
3. **Análisis de Volatilidad:** Detección de regímenes de estabilidad frente a la incertidumbre cambiaria.
4. **Correlaciones:** Comportamiento de las monedas regionales ante el peso chileno.

<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 20px;">
    <strong>Nota:</strong> El dashboard requiere ejecución local o en un servidor Streamlit. El pipeline integrado asegura la actualización de los datos sin intervención manual.
</div>

## Metodología y Fuentes

El cálculo del TCRB sigue el estándar internacional:
$$TCRB = \frac{e \cdot P^*}{P}$$
Donde:
- $e$ representa el tipo de cambio nominal (CLP por moneda extranjera).
- $P^*$ es el nivel de precios (IPC) del país extranjero.
- $P$ es el nivel de precios (IPC) de Chile.

### Gestión de Datos en Cascada
Para garantizar la continuidad de las series, el sistema emplea una arquitectura de respaldo (fallback):
- **Tasas de Cambio:** Banco Central de Chile → Yahoo Finance.
- **Inflación (IPC):** Banco Central de Chile → FRED (St. Louis Fed) → World Bank → INDEC (para Argentina).

La lógica de negocio aborda la complejidad del **Dólar Blue en Argentina**. Esta funcionalidad permite comparar la competitividad de modo oficial frente a la del mercado informal, un factor crítico para el flujo turístico terrestre en el Cono Sur. Como se observa en el análisis de concentración del [**Bar Chart Race: Movimiento Aéreo**](/proyectos/barchart-race/), la estructura del mercado de transporte influye de forma directa en los costos operativos y la competitividad final del destino.

## Implementación Técnica

- **Arquitectura de Micro-servicios:** El código se organiza en capas de extracción (`data`), lógica (`calc`), gráficos (`viz`) e interfaz (`products`).
- **Validación con Pydantic:** Los modelos de datos aseguran que las series descargadas cumplan con los estándares de calidad exigidos.
- **Estandarización:** El uso de un `Makefile` y un CLI `run.py` facilita la reproducción del análisis y el despliegue de los resultados.

---
*Este análisis forma parte de mi portafolio de datos económicos aplicados al sector turismo.*
