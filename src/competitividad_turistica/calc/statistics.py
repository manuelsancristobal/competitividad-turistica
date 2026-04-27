"""Statistical summary tables."""

import logging
import pandas as pd
import numpy as np
from .tcrb import compute_stats

logger = logging.getLogger(__name__)


def summary_table(df: pd.DataFrame, countries: list, stats_dict: dict = None) -> pd.DataFrame:
    """
    Create summary statistics table for all countries.
    """
    if stats_dict is None:
        stats_dict = {}

    rows = []

    for country in countries:
        tcrb_col = f"TCRB_Idx_{country}"

        if tcrb_col not in df.columns:
            continue

        tcrb_idx = df[tcrb_col].dropna()

        if tcrb_idx.empty:
            continue

        # Compute stats
        stats = compute_stats(tcrb_idx)

        row = {
            "País": country,
            "Valor Actual": round(stats.get("actual", np.nan), 2),
            "Mínimo": round(stats.get("min", np.nan), 2),
            "Máximo": round(stats.get("max", np.nan), 2),
            "Promedio": round(stats.get("mean", np.nan), 2),
            "Std Dev": round(stats.get("std", np.nan), 2),
            "Var 12M (%)": round(stats.get("var_12m_pct", np.nan), 2),
            "Percentil": round(stats.get("percentile", np.nan), 1),
            "Z-Score": round(stats.get("zscore", np.nan), 2),
        }

        rows.append(row)

    result = pd.DataFrame(rows)

    logger.info(f"Summary table created: {len(result)} countries")

    return result


def last_n_months(df: pd.DataFrame, countries: list, n: int = 12) -> pd.DataFrame:
    """
    Create table of last N months of raw data and TCRB for all countries.
    """
    # Get last n rows
    df_tail = df.tail(n).copy()

    # Select relevant columns
    cols_to_keep = ["IPC_CHL"]

    for country in countries:
        fx_col = f"FX_{country}"
        ipc_col = f"IPC_{country}"
        tcrb_col = f"TCRB_Idx_{country}"

        for col in [fx_col, ipc_col, tcrb_col]:
            if col in df.columns:
                cols_to_keep.append(col)

    result = df_tail[[c for c in cols_to_keep if c in df_tail.columns]].copy()

    # Round to 2 decimals
    result = result.round(2)

    logger.info(f"Last {n} months table created")

    return result
