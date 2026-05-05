"""Tests for calc/correlation.py."""

import numpy as np
import pandas as pd

from competitividad_turistica.calc.correlation import correlation_matrix, rolling_correlation


class TestCorrelationMatrix:
    def test_returns_two_dataframes(self, sample_dataframe, countries_list):
        corr, pval = correlation_matrix(sample_dataframe, countries_list)
        assert isinstance(corr, pd.DataFrame)
        assert isinstance(pval, pd.DataFrame)

    def test_shape_matches_countries(self, sample_dataframe, countries_list):
        corr, pval = correlation_matrix(sample_dataframe, countries_list)
        assert corr.shape == (3, 3)
        assert pval.shape == (3, 3)

    def test_diagonal_is_one(self, sample_dataframe, countries_list):
        corr, _ = correlation_matrix(sample_dataframe, countries_list)
        np.testing.assert_array_almost_equal(np.diag(corr.values), 1.0)

    def test_symmetric(self, sample_dataframe, countries_list):
        corr, _ = correlation_matrix(sample_dataframe, countries_list)
        np.testing.assert_array_almost_equal(corr.values, corr.values.T)

    def test_values_in_range(self, sample_dataframe, countries_list):
        corr, _ = correlation_matrix(sample_dataframe, countries_list)
        assert (corr.values >= -1).all()
        assert (corr.values <= 1).all()

    def test_insufficient_countries(self, sample_dataframe):
        corr, pval = correlation_matrix(sample_dataframe, ["USA"])
        assert corr.empty
        assert pval.empty

    def test_missing_country_column(self, sample_dataframe):
        corr, pval = correlation_matrix(sample_dataframe, ["USA", "XYZ"])
        # Only USA exists so < 2 valid columns
        assert corr.empty


class TestRollingCorrelation:
    def test_returns_two_series(self, sample_dataframe):
        corr, pval = rolling_correlation(sample_dataframe, "USA", "BRA", window=12)
        assert isinstance(corr, pd.Series)
        assert isinstance(pval, pd.Series)

    def test_values_in_range(self, sample_dataframe):
        corr, _ = rolling_correlation(sample_dataframe, "USA", "BRA", window=12)
        valid = corr.dropna()
        assert (valid >= -1).all()
        assert (valid <= 1).all()

    def test_missing_country(self, sample_dataframe):
        corr, pval = rolling_correlation(sample_dataframe, "USA", "XYZ", window=12)
        assert corr.empty
        assert pval.empty
