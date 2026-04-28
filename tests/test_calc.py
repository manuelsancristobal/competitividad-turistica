import numpy as np
import pandas as pd
import pytest

from competitividad_turistica.calc.tcrb import calculate_tcrb_raw, compute_stats, normalize_index
from competitividad_turistica.data.sources.fred import _inflation_rate_to_cpi_index


def test_calculate_tcrb_raw():
    """Test raw TCRB calculation logic."""
    dates = pd.date_range("2020-01-01", periods=3, freq="MS")
    fx = pd.Series([800.0, 810.0, 820.0], index=dates)
    ipc_foreign = pd.Series([110.0, 112.0, 114.0], index=dates)
    ipc_chile = pd.Series([120.0, 122.0, 125.0], index=dates)

    tcrb = calculate_tcrb_raw(fx, ipc_foreign, ipc_chile)

    # (800 * 110) / 120 = 733.333
    assert pytest.approx(tcrb.iloc[0], 0.01) == 733.33
    # (820 * 114) / 125 = 747.84
    assert pytest.approx(tcrb.iloc[2], 0.01) == 747.84


def test_normalize_index():
    """Test index normalization logic with different base year scenarios."""
    dates = pd.date_range("2015-01-01", periods=24, freq="MS")
    series = pd.Series(np.linspace(100, 123, 24), index=dates)

    # Test with valid base year (2015)
    normalized, effective_year = normalize_index(series, base_year=2015, base=100.0)

    assert effective_year == 2015
    # 2015 average should be ~100
    assert pytest.approx(normalized[normalized.index.year == 2015].mean(), 0.01) == 100.0


def test_inflation_rate_to_cpi_index():
    """Test the conversion from annual inflation rate to monthly CPI."""
    dates = pd.date_range("2020-01-01", periods=2, freq="YS")
    inflation_rate = pd.Series([10.0, 20.0], index=dates)  # 10% in 2020, 20% in 2021

    cpi = _inflation_rate_to_cpi_index(inflation_rate, base=100.0)

    # Check that the index grows over time
    assert len(cpi) == 24
    assert cpi.iloc[0] == 100.0
    assert cpi.iloc[-1] > cpi.iloc[0]


def test_compute_stats():
    """Test calculation of statistics."""
    dates = pd.date_range("2020-01-01", periods=14, freq="MS")
    series = pd.Series(np.linspace(100, 113, 14), index=dates)

    stats = compute_stats(series)

    assert stats["actual"] == 113.0
    assert stats["min"] == 100.0
    assert stats["max"] == 113.0
    assert "var_12m_pct" in stats
