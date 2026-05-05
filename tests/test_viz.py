"""Tests for viz/charts.py — verify chart functions return go.Figure."""

import pandas as pd
import plotly.graph_objects as go

from competitividad_turistica.viz.charts import (
    correlation_heatmap,
    decomposition_chart,
    rolling_correlation_chart,
    tcrb_comparison_chart,
    tcrb_line_chart,
    volatility_chart,
)


class TestTcrbLineChart:
    def test_returns_figure(self, sample_dataframe):
        fig = tcrb_line_chart(sample_dataframe, "USA")
        assert isinstance(fig, go.Figure)

    def test_missing_country_returns_empty_figure(self, sample_dataframe):
        fig = tcrb_line_chart(sample_dataframe, "XYZ")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0


class TestTcrbComparisonChart:
    def test_returns_figure(self, sample_dataframe, countries_list):
        fig = tcrb_comparison_chart(sample_dataframe, countries_list)
        assert isinstance(fig, go.Figure)

    def test_trace_count(self, sample_dataframe, countries_list):
        fig = tcrb_comparison_chart(sample_dataframe, countries_list)
        assert len(fig.data) == 3


class TestCorrelationHeatmap:
    def test_returns_figure(self):
        corr = pd.DataFrame(
            [[1.0, 0.5], [0.5, 1.0]],
            index=["USA", "BRA"],
            columns=["USA", "BRA"],
        )
        fig = correlation_heatmap(corr)
        assert isinstance(fig, go.Figure)

    def test_empty_returns_empty_figure(self):
        fig = correlation_heatmap(pd.DataFrame())
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0


class TestVolatilityChart:
    def test_returns_figure(self, sample_dataframe, sample_tcrb_series):
        from competitividad_turistica.calc.volatility import rolling_volatility

        vol = rolling_volatility(sample_tcrb_series)
        fig = volatility_chart(sample_dataframe, vol, "USA")
        assert isinstance(fig, go.Figure)


class TestRollingCorrelationChart:
    def test_returns_figure(self, sample_dates):
        import numpy as np

        corr = pd.Series(np.random.default_rng(0).uniform(-1, 1, len(sample_dates)), index=sample_dates)
        fig = rolling_correlation_chart(corr, "USA", "BRA")
        assert isinstance(fig, go.Figure)


class TestDecompositionChart:
    def test_empty_returns_empty_figure(self):
        fig = decomposition_chart(pd.DataFrame(), "USA")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0
