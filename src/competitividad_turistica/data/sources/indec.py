"""INDEC (Instituto Nacional de Estadísticas de Argentina) data source for IPC."""

import logging
import time

import pandas as pd
import requests

from competitividad_turistica.config.settings import MAX_REINTENTOS, PAUSA_REINTENTO

from ..cache import cache_key, load_from_cache, save_to_cache
from ..models import DataResult

logger = logging.getLogger(__name__)


def fetch_ipc_indec(start: str, end: str) -> DataResult:
    """
    Fetch Argentine IPC (Índice de Precios al Consumidor) from INDEC public API.

    INDEC provides monthly CPI data from 2017-present via free public API.
    Series ID: 148.3_INIVELNAL_DICI_M_26 (IPC Nacional con variación)

    Args:
        start: Start date (ISO format)
        end: End date (ISO format)

    Returns:
        DataResult with monthly IPC series (index level), or failure status
    """
    country = "ARG"

    # --- Check cache first ---
    key = cache_key(country, "ipc", "indec")
    cached_series, cached_meta = load_from_cache(key)
    if cached_series is not None:
        logger.info("Loaded ARG IPC INDEC from cache")
        return DataResult(
            data=cached_series,
            source="indec (cached)",
            series_id="148.3_INIVELNAL_DICI_M_26",
            country=country,
            variable="ipc",
            coverage=(str(cached_series.index[0])[:10], str(cached_series.index[-1])[:10]),
            obs_count=len(cached_series),
            success=True,
        )

    # --- Download from INDEC API ---
    try:
        url = "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&format=json"

        logger.info("Fetching Argentina IPC from INDEC API")

        for attempt in range(MAX_REINTENTOS):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data_json = response.json()
                break
            except (requests.RequestException, ValueError) as e:
                if attempt < MAX_REINTENTOS - 1:
                    logger.warning(f"INDEC API attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(PAUSA_REINTENTO)
                else:
                    raise Exception(f"INDEC API failed after {MAX_REINTENTOS} attempts: {e}")

        # Parse response
        if "data" not in data_json or len(data_json["data"]) == 0:
            return DataResult(
                data=None,
                source="indec",
                series_id="148.3_INIVELNAL_DICI_M_26",
                country=country,
                variable="ipc",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message="INDEC API returned empty data"
            )

        # Extract series (formato: lista de [fecha, valor])
        series_data = data_json["data"]  # Flat list of [date, value] pairs

        dates = []
        values = []

        for entry in series_data:
            try:
                # entry format: [date_string, value]
                date_str = entry[0]
                value = float(entry[1])

                # INDEC uses format: "2017-01" (YYYY-MM)
                date_obj = pd.to_datetime(date_str)
                dates.append(date_obj)
                values.append(value)
            except (IndexError, ValueError, TypeError):
                continue

        if not values:
            return DataResult(
                data=None,
                source="indec",
                series_id="148.3_INIVELNAL_DICI_M_26",
                country=country,
                variable="ipc",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message="No valid data points extracted from INDEC API"
            )

        # Create series
        series = pd.Series(values, index=pd.DatetimeIndex(dates))
        series = series.sort_index()
        series = series[~series.index.duplicated(keep='first')]

        # Filter to requested date range
        try:
            start_date = pd.to_datetime(start)
            end_date = pd.to_datetime(end)
            series = series[(series.index >= start_date) & (series.index <= end_date)]
        except:
            pass  # Use full range if parsing fails

        if series.empty:
            return DataResult(
                data=None,
                source="indec",
                series_id="148.3_INIVELNAL_DICI_M_26",
                country=country,
                variable="ipc",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message=f"No data in requested range {start} to {end}"
            )

        # Cache the result
        save_to_cache(key, series, {"series_id": "148.3_INIVELNAL_DICI_M_26", "source": "indec"})

        return DataResult(
            data=series,
            source="indec",
            series_id="148.3_INIVELNAL_DICI_M_26",
            country=country,
            variable="ipc",
            coverage=(str(series.index[0])[:10], str(series.index[-1])[:10]),
            obs_count=len(series),
            success=True,
        )

    except Exception as e:
        logger.error(f"INDEC fetch failed: {e}")
        return DataResult(
            data=None,
            source="indec",
            series_id="148.3_INIVELNAL_DICI_M_26",
            country=country,
            variable="ipc",
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e)
        )

