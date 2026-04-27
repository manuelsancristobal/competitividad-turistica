"""Bluelytics data source for Argentine parallel market exchange rate (dólar blue)."""

import logging
import pandas as pd
import requests
import time
from datetime import datetime

from ..models import DataResult
from ..cache import cache_key, load_from_cache, save_to_cache
from competitividad_turistica.config.settings import MAX_REINTENTOS, PAUSA_REINTENTO

logger = logging.getLogger(__name__)


def fetch_fx_bluelytics(start: str, end: str) -> DataResult:
    """
    Fetch Argentine parallel market exchange rate (dólar blue ARS/USD) from Bluelytics API.

    Bluelytics tracks the informal/parallel market rate ARS/USD, which reflects actual
    rates faced by tourists in Argentina (official rates are controlled).

    Returns monthly average of daily blue dollar rates.

    Args:
        start: Start date (ISO format)
        end: End date (ISO format)

    Returns:
        DataResult with monthly ARS_blue/USD series
    """
    country = "ARG"

    # --- Check cache first ---
    key = cache_key(country, "fx_blue", "bluelytics")
    cached_series, cached_meta = load_from_cache(key)
    if cached_series is not None:
        logger.info(f"Loaded ARG blue dollar from cache")
        return DataResult(
            data=cached_series,
            source="bluelytics (cached)",
            series_id="blue_ars_usd",
            country=country,
            variable="fx_blue",
            coverage=(str(cached_series.index[0])[:10], str(cached_series.index[-1])[:10]),
            obs_count=len(cached_series),
            success=True,
        )

    # --- Download from Bluelytics API ---
    try:
        url = "https://api.bluelytics.com.ar/v2/evolution.json"

        logger.info(f"Fetching Argentina blue dollar (ARS/USD) from Bluelytics API")

        for attempt in range(MAX_REINTENTOS):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data_json = response.json()
                break
            except (requests.RequestException, ValueError) as e:
                if attempt < MAX_REINTENTOS - 1:
                    logger.warning(f"Bluelytics API attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(PAUSA_REINTENTO)
                else:
                    raise Exception(f"Bluelytics API failed after {MAX_REINTENTOS} attempts: {e}")

        # Parse response
        # New Bluelytics API returns a flat list of entries:
        # [{"date": "YYYY-MM-DD", "source": "Blue"|"Oficial", "value_sell": float, "value_buy": float}, ...]

        if not isinstance(data_json, list):
             return DataResult(
                data=None,
                source="bluelytics",
                series_id="blue_ars_usd",
                country=country,
                variable="fx_blue",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message="Bluelytics API returned unexpected data format (expected list)"
            )

        blue_entries = [entry for entry in data_json if entry.get("source") == "Blue"]

        if not blue_entries:
            return DataResult(
                data=None,
                source="bluelytics",
                series_id="blue_ars_usd",
                country=country,
                variable="fx_blue",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message="Bluelytics API returned no entries with source='Blue'"
            )

        dates = []
        values = []

        for entry in blue_entries:
            try:
                date_str = entry.get("date")
                # Use average of buy and sell for TCRB calculation
                sell = float(entry.get("value_sell"))
                buy = float(entry.get("value_buy"))
                value = (sell + buy) / 2

                date_obj = pd.to_datetime(date_str)
                dates.append(date_obj)
                values.append(value)
            except (KeyError, ValueError, TypeError, ZeroDivisionError):
                continue

        if not values:
            return DataResult(
                data=None,
                source="bluelytics",
                series_id="blue_ars_usd",
                country=country,
                variable="fx_blue",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message="No valid data points extracted from Bluelytics API"
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
                source="bluelytics",
                series_id="blue_ars_usd",
                country=country,
                variable="fx_blue",
                coverage=("", ""),
                obs_count=0,
                success=False,
                error_message=f"No data in requested range {start} to {end}"
            )

        # Resample to monthly average (first day of month)
        # This ensures alignment with other monthly series
        series_monthly = series.resample("MS").mean()

        # Cache the result
        save_to_cache(key, series_monthly, {"series_id": "blue_ars_usd", "source": "bluelytics"})

        return DataResult(
            data=series_monthly,
            source="bluelytics",
            series_id="blue_ars_usd",
            country=country,
            variable="fx_blue",
            coverage=(str(series_monthly.index[0])[:10], str(series_monthly.index[-1])[:10]),
            obs_count=len(series_monthly),
            success=True,
        )

    except Exception as e:
        logger.error(f"Bluelytics fetch failed: {e}")
        return DataResult(
            data=None,
            source="bluelytics",
            series_id="blue_ars_usd",
            country=country,
            variable="fx_blue",
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e)
        )

