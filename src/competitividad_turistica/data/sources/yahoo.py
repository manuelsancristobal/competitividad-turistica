"""Yahoo Finance data source for exchange rates."""

import logging

import pandas as pd
import yfinance as yf

from ..cache import cache_key, load_from_cache, save_to_cache
from ..models import DataResult

logger = logging.getLogger(__name__)


def fetch_fx_direct(ticker: str, start: str, end: str) -> DataResult:
    """
    Fetch FX directly from Yahoo Finance for a single ticker.
    Returns monthly average.
    """
    try:
        logger.info(f"Fetching {ticker} from Yahoo Finance ({start} to {end})")

        data = yf.download(ticker, start=start, end=end, interval="1d", progress=False)

        if data.empty:
            raise ValueError(f"No data returned for {ticker}")

        # yfinance >=1.2.0 returns MultiIndex columns (Price, Ticker)
        # Flatten to a simple Series
        if isinstance(data.columns, pd.MultiIndex):
            # Try Close price level
            if "Close" in data.columns.get_level_values(0):
                series = data["Close"].iloc[:, 0]
            else:
                series = data.iloc[:, 0]
        else:
            if "Adj Close" in data.columns:
                series = data["Adj Close"]
            elif "Close" in data.columns:
                series = data["Close"]
            else:
                series = data.iloc[:, 0]

        # Ensure it's a 1D Series
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]

        # Resample to monthly average
        series = series.resample("MS").mean()
        series = series.dropna()

        if series.empty:
            raise ValueError(f"No valid data after resampling for {ticker}")

        # Normalize timezone if needed
        if series.index.tz is not None:
            series.index = series.index.tz_localize(None)

        logger.info(f"Successfully fetched {ticker}: {len(series)} monthly observations")

        return DataResult(
            data=series,
            source="yahoo",
            series_id=ticker,
            country="n/a",
            variable="fx",
            coverage=(str(series.index[0])[:10], str(series.index[-1])[:10]),
            obs_count=len(series),
            success=True,
        )

    except Exception as e:
        logger.error(f"Error fetching {ticker} from Yahoo: {e}")
        return DataResult(
            data=None,
            source="yahoo",
            series_id=ticker,
            country="n/a",
            variable="fx",
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e),
        )


def fetch_fx_cross(ticker_pair: tuple, start: str, end: str) -> DataResult:
    """
    Fetch FX via cross-rate: (MON/USD, USD/CLP) to get MON/CLP.
    Both components must be available.
    """
    try:
        ticker_mon_usd, ticker_usd_clp = ticker_pair

        logger.info(f"Fetching cross-rate {ticker_mon_usd} x {ticker_usd_clp}")

        # Fetch both
        result_mon_usd = fetch_fx_direct(ticker_mon_usd, start, end)
        result_usd_clp = fetch_fx_direct(ticker_usd_clp, start, end)

        if not result_mon_usd.success or not result_usd_clp.success:
            raise ValueError("Could not fetch one or both components of cross-rate")

        # Align on intersection of dates
        series_mon_usd = result_mon_usd.data
        series_usd_clp = result_usd_clp.data

        common_dates = series_mon_usd.index.intersection(series_usd_clp.index)

        if len(common_dates) == 0:
            raise ValueError("No common dates between cross-rate components")

        series_mon_usd = series_mon_usd.loc[common_dates]
        series_usd_clp = series_usd_clp.loc[common_dates]

        # Calculate cross-rate: MON/CLP = (MON/USD) x (USD/CLP)
        series = series_mon_usd * series_usd_clp

        # Validate cross-rate is in reasonable range
        median_value = series.median()
        if median_value <= 0:
            logger.warning(f"Cross-rate {ticker_mon_usd}/{ticker_usd_clp} has negative or zero values (median={median_value:.4f})")
        if median_value > 1_000_000:
            logger.warning(f"Cross-rate {ticker_mon_usd}/{ticker_usd_clp} seems extremely high (median={median_value:.2f})")
        if series.isna().sum() > len(series) * 0.2:
            logger.warning(f"Cross-rate {ticker_mon_usd}/{ticker_usd_clp} has >20% NaN values")

        logger.info(f"Successfully computed cross-rate {ticker_mon_usd}/{ticker_usd_clp}: {len(series)} observations")

        return DataResult(
            data=series,
            source="yahoo",
            series_id=f"{ticker_mon_usd}_x_{ticker_usd_clp}",
            country="n/a",
            variable="fx",
            coverage=(str(series.index[0])[:10], str(series.index[-1])[:10]),
            obs_count=len(series),
            success=True,
        )

    except Exception as e:
        logger.error(f"Error computing cross-rate {ticker_pair}: {e}")
        return DataResult(
            data=None,
            source="yahoo",
            series_id=f"{ticker_pair[0]}_x_{ticker_pair[1]}",
            country="n/a",
            variable="fx",
            coverage=("", ""),
            obs_count=0,
            success=False,
            error_message=str(e),
        )


def fetch_fx(country_code: str, fx_ticker_direct: str, fx_ticker_cross: tuple,
             start: str, end: str) -> DataResult:
    """
    Fetch FX for a country, trying direct first, then cross-rate.
    Automatically caches results.
    """

    # Try cache first
    key = cache_key(country_code, "fx", "yahoo")
    cached_series, cached_meta = load_from_cache(key)
    if cached_series is not None:
        return DataResult(
            data=cached_series,
            source="yahoo (cached)",
            series_id=cached_meta["series_id"],
            country=country_code,
            variable="fx",
            coverage=(str(cached_series.index[0])[:10], str(cached_series.index[-1])[:10]),
            obs_count=len(cached_series),
            success=True,
        )

    # Try direct
    if fx_ticker_direct:
        result = fetch_fx_direct(fx_ticker_direct, start, end)
        result.country = country_code
        if result.success:
            save_to_cache(key, result.data, {"source": result.source, "series_id": result.series_id})
            return result

    # Try cross
    if fx_ticker_cross:
        result = fetch_fx_cross(fx_ticker_cross, start, end)
        result.country = country_code
        if result.success:
            save_to_cache(key, result.data, {"source": result.source, "series_id": result.series_id})
            return result

    # Both failed
    return DataResult(
        data=None,
        source="yahoo",
        series_id="unknown",
        country=country_code,
        variable="fx",
        coverage=("", ""),
        obs_count=0,
        success=False,
        error_message="No valid FX ticker (direct or cross) configured",
    )

