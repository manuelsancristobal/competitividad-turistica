"""FRED (Federal Reserve Economic Data) source for CPI data."""

import logging
import time

import pandas as pd
import pandas_datareader.data as web

from competitividad_turistica.config.settings import MAX_REINTENTOS, PAUSA_REINTENTO

from ..cache import cache_key, load_from_cache, save_to_cache
from ..models import DataResult

logger = logging.getLogger(__name__)


def _is_inflation_rate_series(series_id: str) -> bool:
    """Check if a FRED series is an annual inflation rate (not CPI index)."""
    return series_id.startswith("FPCPITOTLZG")


def _inflation_rate_to_cpi_index(inflation_series: pd.Series, base: float = 100.0) -> pd.Series:
    """
    Convert annual inflation rate (%) to a monthly CPI index.
    Assumes constant monthly inflation within each year.
    """
    # Annual inflation → monthly factor
    monthly_factors = (1 + inflation_series / 100) ** (1 / 12)

    cpi_values = []
    dates = []
    current_value = base
    prev_factor = None

    for i, (date, factor) in enumerate(zip(inflation_series.index, monthly_factors)):
        year = date.year
        for month in range(1, 13):  # 1=Jan to 12=Dec
            month_date = pd.Timestamp(year=year, month=month, day=1)

            if i == 0 and month == 1:
                # First month of entire series: base value, no compounding
                cpi_values.append(current_value)
            elif month == 1 and prev_factor is not None:
                # January of subsequent years: 12th compounding of PREVIOUS year
                current_value *= prev_factor
                cpi_values.append(current_value)
            else:
                # Feb-Dec: compound with current year's factor
                current_value *= factor
                cpi_values.append(current_value)

            dates.append(month_date)

        prev_factor = factor

    result = pd.Series(cpi_values, index=pd.DatetimeIndex(dates))
    result = result[~result.index.duplicated(keep='first')]
    return result.sort_index()


def fetch_ipc_fred(series_list: list, start: str, end: str, country: str = "n/a") -> DataResult:
    """
    Fetch IPC from FRED, trying each series in order until one succeeds.
    Returns first successful series. Uses local CSV cache to avoid repeated downloads.
    """
    # --- Check cache first ---
    key = cache_key(country, "ipc", "fred")
    cached_series, cached_meta = load_from_cache(key)
    if cached_series is not None:
        return DataResult(
            data=cached_series,
            source="fred (cached)",
            series_id=cached_meta["series_id"],
            country=country,
            variable="ipc",
            coverage=(str(cached_series.index[0])[:10], str(cached_series.index[-1])[:10]),
            obs_count=len(cached_series),
            success=True,
        )

    # --- No cache: download from FRED ---
    try:
        for series_id in series_list:
            try:
                logger.info(f"Attempting FRED {series_id} ({start} to {end})")

                # Retry logic
                for attempt in range(MAX_REINTENTOS):
                    try:
                        data = web.DataReader(series_id, "fred", start=start, end=end)

                        if data.empty:
                            raise ValueError("Empty data returned")

                        series = data[series_id].dropna()

                        if _is_inflation_rate_series(series_id):
                            # Convert annual inflation rate to CPI index
                            logger.info(f"Converting inflation rate {series_id} to CPI index")
                            series = _inflation_rate_to_cpi_index(series)
                            # Resample to monthly
                            series = series.resample("MS").first()
                        else:
                            # Resample to monthly and interpolate if it's annual data
                            series = series.resample("MS").mean()

                        # Interpolate gaps (e.g. from annual to monthly)
                        if series.isna().any():
                            logger.info(f"Interpolating gaps in FRED series {series_id}")
                            series = series.interpolate(method="linear")

                        series = series.dropna()

                        if len(series) < 12:
                            raise ValueError(f"Insufficient data: {len(series)} observations")

                        logger.info(f"Successfully fetched FRED {series_id}: {len(series)} observations")

                        # --- Save to cache ---
                        save_to_cache(key, series, {"source": "fred", "series_id": series_id})

                        return DataResult(
                            data=series,
                            source="fred",
                            series_id=series_id,
                            country=country,
                            variable="ipc",
                            coverage=(str(series.index[0])[:10], str(series.index[-1])[:10]),
                            obs_count=len(series),
                            success=True,
                        )

                    except Exception as e:
                        if attempt < MAX_REINTENTOS - 1:
                            logger.debug(f"FRED {series_id} attempt {attempt + 1} failed, retrying: {e}")
                            time.sleep(PAUSA_REINTENTO)
                        else:
                            logger.warning(f"FRED {series_id} failed after {MAX_REINTENTOS} attempts: {e}")

            except Exception as e:
                logger.debug(f"FRED {series_id} skipped: {e}")
                continue

        # All series failed
        raise ValueError(f"All {len(series_list)} FRED series failed")

    except Exception as e:
        logger.error(f"Error fetching IPC from FRED for {country}: {e}")
        return DataResult(
            data=None,
            source="fred",
            series_id="|".join(series_list),
            country=country,
            variable="ipc",
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e),
        )


def fetch_ipc_chile(start: str, end: str) -> DataResult:
    """Convenience function for Chile IPC."""
    from competitividad_turistica.config.countries import CHILE_IPC_FRED
    return fetch_ipc_fred(CHILE_IPC_FRED, start, end, country="CHL")

