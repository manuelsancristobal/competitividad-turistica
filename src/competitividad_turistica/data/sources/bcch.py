"""Banco Central de Chile API data source."""

import logging

import pandas as pd

from competitividad_turistica.config.settings import BCCH_PASS, BCCH_USER

from ..cache import cache_key, load_from_cache, save_to_cache
from ..models import DataResult

logger = logging.getLogger(__name__)


def is_available() -> bool:
    """Check if BCCh credentials are configured."""
    return bool(BCCH_USER and BCCH_PASS)


def _fetch_serie(series_id: str, start: str, end: str,
                 country: str, variable: str) -> DataResult:
    """
    Fetch any series from BCCh API (shared logic for FX and IPC).

    Args:
        series_id: BCCh series identifier (e.g. "F072.CLP.ARS.N.O.D")
        start: Start date "YYYY-MM-DD"
        end: End date "YYYY-MM-DD"
        country: Country code (e.g. "ARG", "CHL")
        variable: "fx" or "ipc"
    """
    # --- Check credentials ---
    if not is_available():
        logger.debug("BCCh credentials not available, skipping")
        return DataResult(
            data=None,
            source="bcch",
            series_id=series_id,
            country=country,
            variable=variable,
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message="BCCh credentials not configured",
        )

    # --- Check cache ---
    key = cache_key(country, variable, "bcch")
    cached_series, cached_meta = load_from_cache(key)
    if cached_series is not None:
        return DataResult(
            data=cached_series,
            source="bcch (cached)",
            series_id=cached_meta["series_id"],
            country=country,
            variable=variable,
            coverage=(str(cached_series.index[0])[:10], str(cached_series.index[-1])[:10]),
            obs_count=len(cached_series),
            success=True,
        )

    # --- Download from BCCh ---
    try:
        from bcch import BancoCentralDeChile

        logger.info(f"Fetching BCCh {variable.upper()} {series_id} for {country} ({start} to {end})")

        client = BancoCentralDeChile(BCCH_USER, BCCH_PASS)
        obs_list = client.get_macro(serie=series_id, firstdate=start, lastdate=end)

        if obs_list is None or len(obs_list) == 0:
            raise ValueError(f"No data returned for series {series_id}")

        # Parse response: list of {'indexDateString': 'DD-MM-YYYY', 'value': '...', 'statusCode': 'OK'}
        dates = []
        values = []
        for obs in obs_list:
            if obs.get("statusCode") == "OK":
                try:
                    date = pd.to_datetime(obs["indexDateString"], dayfirst=True)
                    val = float(obs["value"])
                    dates.append(date)
                    values.append(val)
                except (ValueError, TypeError):
                    continue

        if not values:
            raise ValueError(f"No valid observations for series {series_id}")

        series = pd.Series(values, index=pd.DatetimeIndex(dates))
        series = series.sort_index()
        series = series[~series.index.duplicated(keep='first')]
        series = series.resample("MS").mean()
        series = series.dropna()

        if len(series) < 12:
            raise ValueError(f"Insufficient data: {len(series)} observations")

        logger.info(f"Successfully fetched BCCh {variable.upper()} {series_id}: {len(series)} observations")

        # --- Save to cache ---
        save_to_cache(key, series, {"source": "bcch", "series_id": series_id})

        return DataResult(
            data=series,
            source="bcch",
            series_id=series_id,
            country=country,
            variable=variable,
            coverage=(str(series.index[0])[:10], str(series.index[-1])[:10]),
            obs_count=len(series),
            success=True,
        )

    except Exception as e:
        logger.error(f"Error fetching BCCh {variable.upper()} {series_id}: {e}")
        return DataResult(
            data=None,
            source="bcch",
            series_id=series_id,
            country=country,
            variable=variable,
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e),
        )


def fetch_fx(series_id: str, start: str, end: str, country: str = "n/a") -> DataResult:
    """Fetch FX from BCCh API."""
    return _fetch_serie(series_id, start, end, country, variable="fx")


def fetch_ipc(series_id: str, start: str, end: str, country: str = "n/a") -> DataResult:
    """Fetch IPC from BCCh API."""
    return _fetch_serie(series_id, start, end, country, variable="ipc")

