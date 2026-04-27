"""Correlation analysis between countries."""

import logging
import warnings

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def correlation_matrix(df: pd.DataFrame, countries: list) -> tuple:
    """
    Calculate correlation matrix and p-values of TCRB monthly returns between countries.

    Uses Pearson correlation with scipy.stats.pearsonr for significance testing.

    Returns:
        (corr_matrix, pvalue_matrix) - DataFrames with correlations and p-values
    """
    # Extract TCRB indices for selected countries
    tcrb_columns = [f"TCRB_Idx_{c}" for c in countries if f"TCRB_Idx_{c}" in df.columns]

    if len(tcrb_columns) < 2:
        logger.warning("Insufficient countries for correlation analysis")
        return pd.DataFrame(), pd.DataFrame()

    # Monthly returns
    returns = df[tcrb_columns].pct_change(fill_method=None)

    if len(returns.dropna(how='all')) < 2:
        logger.warning("Insufficient data points for correlation analysis")
        return pd.DataFrame(), pd.DataFrame()

    # Calculate correlation matrix with p-values
    n_countries = len(tcrb_columns)
    corr_matrix = np.zeros((n_countries, n_countries))
    pvalue_matrix = np.zeros((n_countries, n_countries))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for i, col1 in enumerate(tcrb_columns):
            for j, col2 in enumerate(tcrb_columns):
                if i == j:
                    corr_matrix[i, j] = 1.0
                    pvalue_matrix[i, j] = 0.0
                else:
                    valid = returns[[col1, col2]].dropna()
                    if len(valid) >= 3:
                        # Check for zero variance
                        if valid[col1].std() < 1e-12 or valid[col2].std() < 1e-12:
                            corr_matrix[i, j] = 0.0
                            pvalue_matrix[i, j] = 1.0
                        else:
                            try:
                                corr, pval = stats.pearsonr(valid[col1], valid[col2])
                                corr_matrix[i, j] = corr
                                pvalue_matrix[i, j] = pval
                            except:
                                corr_matrix[i, j] = np.nan
                                pvalue_matrix[i, j] = np.nan
                    else:
                        corr_matrix[i, j] = np.nan
                        pvalue_matrix[i, j] = np.nan

    # Convert to DataFrames
    country_codes = [col.replace("TCRB_Idx_", "") for col in tcrb_columns]
    corr_df = pd.DataFrame(corr_matrix, index=country_codes, columns=country_codes)
    pval_df = pd.DataFrame(pvalue_matrix, index=country_codes, columns=country_codes)

    logger.info(f"Correlation matrix with p-values calculated for {len(tcrb_columns)} countries")

    return corr_df, pval_df


def rolling_correlation(df: pd.DataFrame, c1: str, c2: str, window: int = 24) -> tuple:
    """
    Calculate rolling correlation and p-values between two countries.

    Returns:
        (rolling_corr, rolling_pval) - Series with rolling correlations and p-values
    """
    col1 = f"TCRB_Idx_{c1}"
    col2 = f"TCRB_Idx_{c2}"

    if col1 not in df.columns or col2 not in df.columns:
        logger.warning(f"Missing data for rolling correlation {c1}-{c2}")
        return pd.Series(dtype=float), pd.Series(dtype=float)

    # Monthly returns
    returns1 = df[col1].pct_change(fill_method=None)
    returns2 = df[col2].pct_change(fill_method=None)

    # Rolling correlation (Pandas method)
    rolling_corr = returns1.rolling(window=window).corr(returns2)

    # Rolling p-value (using scipy for each window)
    rolling_pval = pd.Series(index=returns1.index, dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for idx in range(window - 1, len(returns1)):
            window_r1 = returns1.iloc[idx - window + 1:idx + 1]
            window_r2 = returns2.iloc[idx - window + 1:idx + 1]

            if len(window_r1) >= 3 and window_r1.notna().all() and window_r2.notna().all():
                try:
                    # Check for zero variance
                    if window_r1.std() < 1e-12 or window_r2.std() < 1e-12:
                        rolling_pval.iloc[idx] = 1.0
                    else:
                        _, pval = stats.pearsonr(window_r1, window_r2)
                        rolling_pval.iloc[idx] = pval
                except:
                    rolling_pval.iloc[idx] = np.nan
            else:
                rolling_pval.iloc[idx] = np.nan

    logger.info(f"Rolling correlation {c1}-{c2} ({window}M) with p-values calculated")

    return rolling_corr, rolling_pval
