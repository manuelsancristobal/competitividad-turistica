"""Tests for calc/statistics.py."""

import pandas as pd

from competitividad_turistica.calc.statistics import last_n_months, summary_table


class TestSummaryTable:
    def test_returns_dataframe(self, sample_dataframe, countries_list):
        result = summary_table(sample_dataframe, countries_list)
        assert isinstance(result, pd.DataFrame)

    def test_has_expected_columns(self, sample_dataframe, countries_list):
        result = summary_table(sample_dataframe, countries_list)
        expected_cols = {"País", "Valor Actual", "Mínimo", "Máximo", "Promedio"}
        assert expected_cols.issubset(set(result.columns))

    def test_row_count_matches_available_countries(self, sample_dataframe, countries_list):
        result = summary_table(sample_dataframe, countries_list)
        assert len(result) == 3

    def test_missing_country_excluded(self, sample_dataframe):
        result = summary_table(sample_dataframe, ["USA", "XYZ"])
        assert len(result) == 1

    def test_empty_dataframe(self, countries_list):
        df = pd.DataFrame()
        result = summary_table(df, countries_list)
        assert result.empty


class TestLastNMonths:
    def test_returns_last_n_rows(self, sample_dataframe, countries_list):
        result = last_n_months(sample_dataframe, countries_list, n=6)
        assert len(result) == 6

    def test_contains_ipc_chl(self, sample_dataframe, countries_list):
        result = last_n_months(sample_dataframe, countries_list, n=6)
        assert "IPC_CHL" in result.columns

    def test_values_are_rounded(self, sample_dataframe, countries_list):
        result = last_n_months(sample_dataframe, countries_list, n=6)
        # Check that values have at most 2 decimals
        for col in result.columns:
            for val in result[col].dropna():
                assert round(val, 2) == val
