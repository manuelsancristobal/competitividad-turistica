"""Seasonal analysis of TCRB."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def monthly_pattern(tcrb_index: pd.Series) -> pd.DataFrame:
    """
    Analyze monthly seasonal patterns in TCRB.
    Returns DataFrame with monthly statistics.
    """
    tcrb_index = tcrb_index.dropna()

    if tcrb_index.empty:
        return pd.DataFrame()

    # Extract month from index
    months = tcrb_index.index.month
    years = tcrb_index.index.year

    # Group by month
    monthly_stats = []

    for month in range(1, 13):
        month_data = tcrb_index[months == month]

        if len(month_data) > 0:
            stats = {
                "month": month,
                "month_name": ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"][month - 1],
                "mean": month_data.mean(),
                "std": month_data.std(),
                "min": month_data.min(),
                "max": month_data.max(),
                "n_obs": len(month_data),
            }
            monthly_stats.append(stats)

    result_df = pd.DataFrame(monthly_stats)

    # Identify best and worst months using idxmin/idxmax (robust against float comparison)
    result_df["is_best"] = False
    result_df["is_worst"] = False
    if not result_df.empty and result_df["mean"].notna().any():
        best_idx = result_df["mean"].idxmin()   # TCRB bajo = más competitivo
        worst_idx = result_df["mean"].idxmax()   # TCRB alto = menos competitivo
        result_df.loc[best_idx, "is_best"] = True
        result_df.loc[worst_idx, "is_worst"] = True

    logger.info(f"Monthly pattern analyzed: {len(result_df)} months")

    return result_df
