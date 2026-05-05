"""Tests for calc/volatility.py."""

import numpy as np
import pandas as pd

from competitividad_turistica.calc.volatility import rolling_volatility, volatility_regime


class TestRollingVolatility:
    def test_returns_series(self, sample_tcrb_series):
        result = rolling_volatility(sample_tcrb_series, window=12)
        assert isinstance(result, pd.Series)

    def test_length_matches_input(self, sample_tcrb_series):
        result = rolling_volatility(sample_tcrb_series, window=12)
        assert len(result) == len(sample_tcrb_series)

    def test_first_values_are_nan(self, sample_tcrb_series):
        result = rolling_volatility(sample_tcrb_series, window=12)
        # First 12 values should be NaN (window + pct_change)
        assert result.iloc[:12].isna().all()

    def test_non_negative(self, sample_tcrb_series):
        result = rolling_volatility(sample_tcrb_series, window=12)
        valid = result.dropna()
        assert (valid >= 0).all()

    def test_annualized_larger(self, sample_tcrb_series):
        ann = rolling_volatility(sample_tcrb_series, window=12, annualized=True)
        monthly = rolling_volatility(sample_tcrb_series, window=12, annualized=False)
        # Annualized should be sqrt(12) times monthly
        ratio = ann.dropna() / monthly.dropna()
        np.testing.assert_array_almost_equal(ratio.values, np.sqrt(12), decimal=5)

    def test_empty_input(self):
        result = rolling_volatility(pd.Series(dtype=float))
        assert result.empty


class TestVolatilityRegime:
    def test_returns_string_series(self, sample_tcrb_series):
        vol = rolling_volatility(sample_tcrb_series, window=12)
        regime = volatility_regime(vol)
        assert regime.dtype == object

    def test_valid_labels(self, sample_tcrb_series):
        vol = rolling_volatility(sample_tcrb_series, window=12)
        regime = volatility_regime(vol)
        valid = regime.dropna()
        assert set(valid.unique()).issubset({"baja", "media", "alta"})

    def test_empty_input(self):
        result = volatility_regime(pd.Series(dtype=float))
        assert result.empty
