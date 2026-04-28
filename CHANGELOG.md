# Changelog

En este archivo puedes encontrar todos los cambios notables de este proyecto.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [0.1.0] - 2026-04-26

### Added
- Reestructuración del proyecto siguiendo el estándar avanzado del portafolio.
- Nuevo punto de entrada unificado `run.py` con comandos `assets`, `deploy`, `ver`, `test`.
- Configuración de Setuptools (`pyproject.toml`) reemplazando a Poetry.
- Makefile estandarizado para flujo de trabajo local.
- Integración de pre-commit hooks (ruff, nbstripout).
- Soporte para despliegue automatizado al repositorio Jekyll del portafolio.
- Configuración de CI con GitHub Actions.
- Pipeline de datos automatizado para TCRB (Tipo de Cambio Real Bilateral).
- Dashboard interactivo con Streamlit para análisis de competitividad.

### Changed
- Código fuente movido a `src/competitividad_turistica/`.
- Actualización de todas las rutas de importación al formato de paquete.
- Migración de dependencias de `pyproject.toml` (Poetry) a formato estándar Setuptools.
