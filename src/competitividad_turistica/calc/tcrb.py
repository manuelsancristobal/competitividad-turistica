"""Core TCRB calculation and index normalization."""

import logging

import numpy as np
import pandas as pd

from competitividad_turistica.config.settings import BASE_INDEX, BASE_YEAR

logger = logging.getLogger(__name__)


def calculate_tcrb_raw(fx: pd.Series, ipc_foreign: pd.Series, ipc_chile: pd.Series) -> pd.Series:
    """
    Calculate raw TCRB = (E x P_i) / P_CL
    where:
      E = nominal exchange rate (currency units per 1 CLP)
      P_i = foreign country CPI
      P_CL = Chile CPI
    """
    # Align on intersection of dates
    common_dates = fx.index.intersection(ipc_foreign.index).intersection(ipc_chile.index)

    fx_aligned = fx.loc[common_dates]
    ipc_foreign_aligned = ipc_foreign.loc[common_dates]
    ipc_chile_aligned = ipc_chile.loc[common_dates]

    tcrb = (fx_aligned * ipc_foreign_aligned) / ipc_chile_aligned

    return tcrb


def normalize_index(series: pd.Series, base_year: int = BASE_YEAR, base: float = BASE_INDEX) -> tuple:
    """
    Normalize series to index with specified base (default 100).
    Uses base_year (default 2015) average as base period.

    Fallback logic:
    - If base_year has >=6 months of data: use its average
    - Else: use average of (base_year-1, base_year, base_year+1)

    Returns:
        (indexed_series, effective_base_year)
    """
    series_clean = series.dropna()
    if series_clean.empty:
        logger.warning("Empty series, cannot normalize")
        return series, None

    # Try to use base_year
    base_year_data = series_clean[series_clean.index.year == base_year]

    if len(base_year_data) >= 6:
        # Good coverage in base_year
        base_mean = base_year_data.mean()
        effective_base_year = base_year
        logger.info(f"Using {base_year} as base year ({len(base_year_data)} months)")
    else:
        # Fallback: use (base_year-1, base_year, base_year+1) average
        fallback_data = series_clean[
            (series_clean.index.year >= base_year - 1) & (series_clean.index.year <= base_year + 1)
        ]

        if len(fallback_data) >= 6:
            base_mean = fallback_data.mean()
            effective_base_year = base_year  # Report as base_year for consistency
            logger.info(f"Fallback: using {base_year - 1}–{base_year + 1} average ({len(fallback_data)} months)")
        else:
            # Last resort: use first year average (backward compatible)
            first_year = series_clean.index[0].year
            first_year_data = series_clean[series_clean.index.year == first_year]
            if len(first_year_data) == 0:
                logger.warning("No data available for base period")
                return series, None
            base_mean = first_year_data.mean()
            effective_base_year = first_year
            logger.warning(f"No data in {base_year}, using first available year {first_year}")

    if base_mean == 0 or np.isnan(base_mean):
        logger.warning("Base year mean is zero or NaN, cannot normalize")
        return series, None

    indexed = (series / base_mean) * base

    return indexed, effective_base_year


def calculate_tcrb_all(df: pd.DataFrame, countries: list) -> tuple:
    """
    Calculate TCRB and derived series for all countries.
    Adds columns:
    - TCRB_Raw_{country}
    - TCRB_Idx_{country}
    - TCRB_MA12_{country}

    Returns:
        (result_df, base_years_dict) where base_years_dict maps country_code to effective base year
    """
    logger.info("Calculating TCRB for all countries")

    result_df = df.copy()
    base_years = {}

    for country in countries:
        try:
            fx_col = f"FX_{country}"
            ipc_col = f"IPC_{country}"
            ipc_chl_col = "IPC_CHL"

            if fx_col not in df.columns or ipc_col not in df.columns or ipc_chl_col not in df.columns:
                logger.warning(f"Missing data for {country}, skipping")
                continue

            # Calculate raw TCRB
            tcrb_raw = calculate_tcrb_raw(df[fx_col], df[ipc_col], df[ipc_chl_col])

            # Normalize to index (now returns tuple with effective base year)
            tcrb_idx, effective_base_year = normalize_index(tcrb_raw, base_year=BASE_YEAR, base=BASE_INDEX)
            base_years[country] = effective_base_year

            # Moving average
            tcrb_ma12 = tcrb_idx.rolling(window=12, center=False).mean()

            # Add to result
            result_df[f"TCRB_Raw_{country}"] = tcrb_raw
            result_df[f"TCRB_Idx_{country}"] = tcrb_idx
            result_df[f"TCRB_MA12_{country}"] = tcrb_ma12

            # Handle parallel FX if exists (e.g., Argentina Blue)
            fx_blue_col = f"FX_{country}_BLUE"
            if fx_blue_col in df.columns:
                tcrb_raw_blue = calculate_tcrb_raw(df[fx_blue_col], df[ipc_col], df[ipc_chl_col])
                tcrb_idx_blue, _ = normalize_index(tcrb_raw_blue, base_year=BASE_YEAR, base=BASE_INDEX)
                tcrb_ma12_blue = tcrb_idx_blue.rolling(window=12).mean()

                result_df[f"TCRB_Raw_{country}_BLUE"] = tcrb_raw_blue
                result_df[f"TCRB_Idx_{country}_BLUE"] = tcrb_idx_blue
                result_df[f"TCRB_MA12_{country}_BLUE"] = tcrb_ma12_blue
                logger.info(f"TCRB (Blue) calculated for {country}")

            logger.info(f"TCRB calculated for {country} (base year: {effective_base_year})")

        except Exception as e:
            logger.error(f"Error calculating TCRB for {country}: {e}")

    return result_df, base_years


def compute_stats(tcrb_index: pd.Series) -> dict:
    """
    Compute statistical summary for a TCRB series.
    """
    if tcrb_index.empty:
        return {}

    # 12-month change
    var_12m = (
        ((tcrb_index.iloc[-1] - tcrb_index.iloc[-13]) / tcrb_index.iloc[-13] * 100) if len(tcrb_index) > 12 else np.nan
    )

    stats = {
        "actual": float(tcrb_index.iloc[-1]),
        "min": float(tcrb_index.min()),
        "max": float(tcrb_index.max()),
        "mean": float(tcrb_index.mean()),
        "std": float(tcrb_index.std()),
        "var_12m_pct": float(var_12m),
        "percentile": float((tcrb_index <= tcrb_index.iloc[-1]).sum() / len(tcrb_index) * 100),
        "date_last": str(tcrb_index.index[-1].date()),
        "zscore": float((tcrb_index.iloc[-1] - tcrb_index.mean()) / tcrb_index.std()) if tcrb_index.std() > 0 else 0,
    }

    return stats


def calculate_hp_filter(tcrb_index: pd.Series, lamb: int = 1600) -> pd.Series:
    """
    Calculate Hodrick-Prescott filter trend for TCRB index.

    The HP filter extracts the trend (non-stationary) component from the series
    without the lag that moving averages introduce.

    Args:
        tcrb_index: TCRB index series
        lamb: Smoothing parameter (default 1600 for monthly data, standard for central banks)

    Returns:
        Trend component (same index as input)
    """
    if tcrb_index.empty or len(tcrb_index) < 8:
        logger.warning("Insufficient data for HP filter")
        return tcrb_index.copy()

    try:
        from statsmodels.tsa.filters.hp_filter import hpfilter
    except ImportError:
        logger.error("statsmodels not installed, cannot compute HP filter")
        return tcrb_index.copy()

    try:
        trend, cycle = hpfilter(tcrb_index.dropna(), lamb=lamb)
        # Align back to original index
        trend_aligned = pd.Series(index=tcrb_index.index, dtype=float)
        trend_aligned.loc[tcrb_index.notna()] = trend.values
        logger.info(f"HP filter (λ={lamb}) calculated")
        return trend_aligned
    except Exception as e:
        logger.error(f"HP filter calculation failed: {e}")
        return tcrb_index.copy()
