"""World Bank data source for CPI fallback."""

import logging

import pandas as pd
import wbgapi as wb

from ..cache import cache_key, load_from_cache, save_to_cache
from ..models import DataResult

logger = logging.getLogger(__name__)


def fetch_ipc_worldbank(country_code: str, start: str, end: str) -> DataResult:
    """
    Fetch CPI from World Bank (annual data, interpolated to monthly).
    Uses local CSV cache to avoid repeated downloads.
    """
    # --- Check cache first ---
    key = cache_key(country_code, "ipc", "worldbank")
    cached_series, cached_meta = load_from_cache(key)
    if cached_series is not None:
        return DataResult(
            data=cached_series,
            source="worldbank (cached)",
            series_id=cached_meta["series_id"],
            country=country_code,
            variable="ipc",
            coverage=(str(cached_series.index[0])[:10], str(cached_series.index[-1])[:10]),
            obs_count=len(cached_series),
            success=True,
        )

    # --- No cache: download from World Bank ---
    try:
        logger.info(f"Fetching World Bank CPI for {country_code}")

        # World Bank CPI indicator
        indicator = "FP.CPI.TOTL"

        start_year = int(start[:4])
        end_year = int(end[:4])

        # Get data using wbgapi
        try:
            df = wb.data.DataFrame(
                indicator,
                economy=country_code,
                time=range(start_year, end_year + 1),
            )

            if df is None or df.empty:
                raise ValueError("No data returned from World Bank")

            # df has years as columns (YR2000, YR2001, etc.) and country as index
            # Transpose to get years as rows
            series = df.iloc[0]  # First (only) row
            series = series.dropna()

            if len(series) < 5:
                raise ValueError(f"Insufficient annual data: {len(series)} years")

            # Convert index from 'YR2000' format to datetime
            dates = []
            values = []
            for idx, val in series.items():
                year_str = str(idx).replace("YR", "")
                try:
                    dates.append(pd.Timestamp(f"{year_str}-01-01"))
                    values.append(float(val))
                except (ValueError, TypeError):
                    continue

            if len(dates) < 5:
                raise ValueError(f"Insufficient parseable data: {len(dates)} years")

            annual_series = pd.Series(values, index=pd.DatetimeIndex(dates))
            annual_series = annual_series.sort_index()

        except Exception as e:
            logger.warning(f"wbgapi DataFrame method failed: {e}, trying alternative")
            # Alternative: use wb.data.fetch
            records = []
            for row in wb.data.fetch(indicator, economy=country_code,
                                      time=range(start_year, end_year + 1)):
                if row.get("value") is not None:
                    year = int(str(row["time"]).replace("YR", ""))
                    records.append((pd.Timestamp(f"{year}-01-01"), float(row["value"])))

            if len(records) < 5:
                raise ValueError(f"Insufficient data from World Bank: {len(records)} years")

            records.sort(key=lambda x: x[0])
            annual_series = pd.Series(
                [r[1] for r in records],
                index=pd.DatetimeIndex([r[0] for r in records])
            )

        # Interpolate from annual to monthly using cubic spline
        date_range = pd.date_range(
            start=f"{start_year}-01-01",
            end=f"{end_year}-12-01",
            freq="MS"
        )

        # Reindex annual data to monthly
        series_monthly = annual_series.reindex(date_range)

        # Interpolate missing months (linear doesn't require scipy)
        series_monthly = series_monthly.interpolate(method="linear")
        series_monthly = series_monthly.ffill().bfill()
        series_monthly = series_monthly.dropna()

        logger.info(f"Interpolated World Bank CPI for {country_code}: {len(series_monthly)} monthly observations")

        # --- Save to cache ---
        save_to_cache(key, series_monthly, {"source": "worldbank", "series_id": indicator})

        return DataResult(
            data=series_monthly,
            source="worldbank",
            series_id=indicator,
            country=country_code,
            variable="ipc",
            coverage=(str(series_monthly.index[0])[:10], str(series_monthly.index[-1])[:10]),
            obs_count=len(series_monthly),
            success=True,
        )

    except Exception as e:
        logger.error(f"Error fetching World Bank CPI for {country_code}: {e}")
        return DataResult(
            data=None,
            source="worldbank",
            series_id="FP.CPI.TOTL",
            country=country_code,
            variable="ipc",
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e),
        )
