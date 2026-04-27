"""Volatility analysis of TCRB."""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def rolling_volatility(tcrb_index: pd.Series, window: int = 12, annualized: bool = True) -> pd.Series:
    """
    Calculate rolling standard deviation (volatility) of TCRB monthly returns.

    Args:
        tcrb_index: Time series of TCRB index values
        window: Rolling window size in months (default 12)
        annualized: If True (default), multiply by √12 to annualize the volatility

    Returns:
        Rolling volatility series expressed as percentage (%)
        Note: Values are annualized by default (√12 factor). Use annualized=False for monthly volatility.
    """
    if tcrb_index.empty:
        return pd.Series(dtype=float)

    # Monthly returns
    returns = tcrb_index.pct_change(fill_method=None)

    # Rolling std of returns (multiply by 100 to express as %)
    rolling_std = returns.rolling(window=window, center=False).std() * 100

    # Annualize volatility if requested (multiply by sqrt(12) for 12-month window)
    if annualized:
        rolling_std = rolling_std * np.sqrt(12)
        annualization_note = " (annualized by sqrt(12))"
    else:
        annualization_note = " (monthly)"

    logger.info(f"Rolling volatility ({window}M){annualization_note} calculated")

    return rolling_std


def volatility_regime(vol_series: pd.Series) -> pd.Series:
    """
    Classify volatility into regimes: low / medium / high.
    Using percentiles: 0-33% = low, 33-67% = medium, 67-100% = high.
    """
    if vol_series.empty or vol_series.dropna().empty:
        return pd.Series(index=vol_series.index, dtype=str)

    # Remove NaN for percentile calculation
    vol_clean = vol_series.dropna()

    p33 = vol_clean.quantile(0.33)
    p67 = vol_clean.quantile(0.67)

    regime = pd.Series(index=vol_series.index, dtype=str)

    regime[vol_series <= p33] = "baja"
    regime[(vol_series > p33) & (vol_series <= p67)] = "media"
    regime[vol_series > p67] = "alta"

    logger.info(f"Volatility regimes assigned (low: <={p33:.2f}%, medium: {p33:.2f}-{p67:.2f}%, high: >{p67:.2f}%)")

    return regime
