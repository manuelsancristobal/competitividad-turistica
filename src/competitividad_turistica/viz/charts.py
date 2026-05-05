"""Plotly chart generation for TCRB analysis."""

import logging

import pandas as pd
import plotly.graph_objects as go

from .theme import (
    ACCENT_MID,
    BASELINE_COLOR,
    add_footnote,
    apply_theme,
    get_country_color,
    get_country_name,
    source_footnote,
)

logger = logging.getLogger(__name__)


def tcrb_line_chart(
    df: pd.DataFrame,
    country: str,
    show_ma12: bool = True,
    perspective: str = "emissive",
    source_registry: dict = None,
) -> go.Figure:
    """Single-country TCRB time series chart."""
    tcrb_col = f"TCRB_Idx_{country}"
    ma12_col = f"TCRB_MA12_{country}"

    if tcrb_col not in df.columns:
        logger.warning(f"Column {tcrb_col} not found")
        return go.Figure()

    fig = go.Figure()

    color = get_country_color(country)
    country_name = get_country_name(country)

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[tcrb_col],
            mode="lines",
            name="TCRB",
            line=dict(color=color, width=2.5),
            hovertemplate="%{x|%Y-%m}<br>%{y:.1f}<extra></extra>",
        )
    )

    if show_ma12 and ma12_col in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[ma12_col],
                mode="lines",
                name="MA 12M",
                line=dict(color=color, width=1.5, dash="dash"),
                hovertemplate="%{x|%Y-%m}<br>%{y:.1f}<extra></extra>",
            )
        )

    fig.add_hline(y=100, line_dash="solid", line_color=BASELINE_COLOR, line_width=1.5)

    fig.update_layout(height=550, yaxis_title="Índice (2015=100)")

    apply_theme(fig, title=f"TCRB — {country_name}")

    if source_registry:
        footnote_text = source_footnote(source_registry, country)
        add_footnote(fig, footnote_text)

    return fig


def tcrb_comparison_chart(
    df: pd.DataFrame,
    countries: list,
    source_registry: dict = None,
) -> go.Figure:
    """Multi-country TCRB comparison chart."""
    fig = go.Figure()

    for country in countries:
        tcrb_col = f"TCRB_Idx_{country}"

        if tcrb_col not in df.columns:
            logger.warning(f"Column {tcrb_col} not found")
            continue

        color = get_country_color(country)
        country_name = get_country_name(country)

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[tcrb_col],
                mode="lines",
                name=country_name,
                line=dict(color=color, width=2),
                hovertemplate="<b>%{fullData.name}</b><br>%{x|%Y-%m}: %{y:.1f}<extra></extra>",
            )
        )

    fig.add_hline(y=100, line_dash="solid", line_color=BASELINE_COLOR, line_width=1.5)

    fig.update_layout(height=550, yaxis_title="Índice (2015=100)")

    apply_theme(fig, title="Competitividad Turística Bilateral")
    add_footnote(fig, "Fuente: BCCh, FRED, Yahoo Finance, World Bank | Base 2015=100")

    return fig


def decomposition_chart(decomp_df: pd.DataFrame, country: str) -> go.Figure:
    """Decomposition chart: stacked bar chart for components + line for total."""
    if decomp_df.empty:
        return go.Figure()

    country_name = get_country_name(country)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=decomp_df.index,
            y=decomp_df["efecto_cambiario"],
            name="Efecto Cambiario",
            marker_color="rgba(100, 116, 139, 0.7)",  # Slate 500
        )
    )

    fig.add_trace(
        go.Bar(
            x=decomp_df.index,
            y=decomp_df["efecto_inflacion"],
            name="Efecto Inflación",
            marker_color="rgba(148, 163, 184, 0.7)",  # Slate 400
        )
    )

    fig.add_trace(
        go.Scatter(
            x=decomp_df.index,
            y=decomp_df["var_tcrb"],
            mode="lines",
            name="Variación Total",
            line=dict(color="#1E293B", width=2),
            yaxis="y2",
        )
    )

    fig.update_layout(
        yaxis_title="Efecto (%)",
        yaxis2=dict(title="Var. Total (%)", overlaying="y", side="right", showgrid=False),
        barmode="stack",
        height=550,
    )

    apply_theme(fig, title=f"Descomposición — {country_name}")
    add_footnote(fig, "Variación interanual (YoY). Descomposición multiplicativa.")

    return fig


def seasonality_chart(monthly_df: pd.DataFrame, country: str) -> go.Figure:
    """Seasonality chart: box plot of monthly patterns."""
    if monthly_df.empty:
        return go.Figure()

    country_name = get_country_name(country)
    color = get_country_color(country)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=monthly_df["month_name"],
            y=monthly_df["mean"],
            error_y=dict(
                type="data",
                array=monthly_df["std"],
                visible=True,
            ),
            marker_color=color,
            name="Promedio ± Std Dev",
        )
    )

    fig.update_layout(
        title=f"Patrón Estacional {country_name}",
        xaxis_title="Mes",
        yaxis_title="TCRB Promedio",
        height=400,
    )

    apply_theme(fig)

    return fig


def volatility_chart(
    df: pd.DataFrame,
    vol_series: pd.Series,
    country: str,
) -> go.Figure:
    """Volatility chart: rolling volatility with bands."""
    if vol_series.empty or vol_series.dropna().empty:
        return go.Figure()

    country_name = get_country_name(country)
    color = get_country_color(country)

    mean_vol = vol_series.mean()
    std_vol = vol_series.std()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=vol_series.index,
            y=vol_series,
            mode="lines",
            name="Volatilidad Rolling 12M",
            line=dict(color=color, width=2),
        )
    )

    fig.add_hline(
        y=mean_vol,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Promedio: {mean_vol:.2f}%",
    )

    fig.add_hline(
        y=mean_vol + std_vol,
        line_dash="dot",
        line_color="lightgrey",
        annotation_text=f"Media + 1σ: {mean_vol + std_vol:.2f}%",
    )

    fig.update_layout(
        title=f"Volatilidad {country_name} (Rolling 12M)",
        xaxis_title="Fecha",
        yaxis_title="Volatilidad (%)",
        height=400,
    )

    apply_theme(fig)

    return fig


def correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Correlation matrix heatmap."""
    if corr_matrix.empty:
        return go.Figure()

    # Replace country codes with names in labels
    labels = [get_country_name(c) for c in corr_matrix.columns]

    # Muted RdBu colorscale
    colorscale = [
        [0.0, "#B91C1C"],
        [0.25, "#DC8A8A"],
        [0.5, "#FFFFFF"],
        [0.75, "#8AB4DC"],
        [1.0, "#1D4ED8"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=labels,
            y=labels,
            colorscale=colorscale,
            zmid=0,
            zmin=-1,
            zmax=1,
            text=corr_matrix.values.round(2),
            texttemplate="%{text:.2f}",
            textfont={"size": 10, "color": ACCENT_MID},
        )
    )

    fig.update_layout(height=550, xaxis=dict(side="bottom"), yaxis=dict(autorange="reversed"))

    apply_theme(fig, title="Correlación — Retornos Mensuales")
    add_footnote(fig, "Correlación de Pearson sobre retornos mensuales del TCRB.")

    return fig


def rolling_correlation_chart(rolling_corr: pd.Series, c1: str, c2: str) -> go.Figure:
    """Rolling pairwise correlation chart."""
    if rolling_corr.empty:
        return go.Figure()

    c1_name = get_country_name(c1)
    c2_name = get_country_name(c2)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=rolling_corr.index,
            y=rolling_corr,
            mode="lines",
            name=f"{c1_name} vs {c2_name}",
            line=dict(color="steelblue", width=2),
        )
    )

    fig.add_hline(y=0, line_dash="dash", line_color="grey")

    fig.update_layout(
        title=f"Correlación Rolling 24M: {c1_name} vs {c2_name}",
        xaxis_title="Fecha",
        yaxis_title="Correlación",
        height=400,
    )

    apply_theme(fig)

    return fig
