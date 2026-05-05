"""Shared test fixtures for competitividad-turistica."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_dates():
    """Monthly date range for testing."""
    return pd.date_range("2020-01-01", periods=36, freq="MS")


@pytest.fixture
def sample_tcrb_series(sample_dates):
    """Synthetic TCRB index series around base 100."""
    rng = np.random.default_rng(42)
    values = 100 + np.cumsum(rng.normal(0, 2, len(sample_dates)))
    return pd.Series(values, index=sample_dates, name="TCRB_Idx_USA")


@pytest.fixture
def sample_dataframe(sample_dates):
    """DataFrame with TCRB indices for multiple countries."""
    rng = np.random.default_rng(42)
    n = len(sample_dates)
    df = pd.DataFrame(
        {
            "TCRB_Idx_USA": 100 + np.cumsum(rng.normal(0, 2, n)),
            "TCRB_Idx_BRA": 100 + np.cumsum(rng.normal(0, 3, n)),
            "TCRB_Idx_ARG": 100 + np.cumsum(rng.normal(0, 4, n)),
            "IPC_CHL": 100 + np.cumsum(rng.normal(0.3, 0.1, n)),
            "IPC_USA": 100 + np.cumsum(rng.normal(0.2, 0.1, n)),
            "FX_USA": 800 + np.cumsum(rng.normal(0, 10, n)),
        },
        index=sample_dates,
    )
    return df


@pytest.fixture
def countries_list():
    """Sample country list for tests."""
    return ["USA", "BRA", "ARG"]
