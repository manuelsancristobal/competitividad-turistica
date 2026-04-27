"""Plotly table generation."""

import logging

import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def summary_stats_table(stats_df: pd.DataFrame) -> go.Figure:
    """
    Create Plotly table with summary statistics.
    """
    if stats_df.empty:
        logger.warning("Empty statistics DataFrame")
        return go.Figure()

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(stats_df.columns),
                    fill_color="steelblue",
                    align="center",
                    font=dict(color="white", size=12),
                ),
                cells=dict(
                    values=[stats_df[col] for col in stats_df.columns],
                    fill_color="lavender",
                    align="center",
                    font=dict(size=11),
                ),
            )
        ]
    )

    fig.update_layout(
        title="Estadísticas Resumen TCRB",
        height=300 + len(stats_df) * 30,
    )

    return fig


def last_12_months_table(data_df: pd.DataFrame) -> go.Figure:
    """
    Create Plotly table with last 12 months of data.
    """
    if data_df.empty:
        logger.warning("Empty data DataFrame")
        return go.Figure()

    # Reset index to make date a column
    df_display = data_df.reset_index()
    df_display.columns = ["Fecha"] + [col.replace("_", " ") for col in df_display.columns[1:]]

    # Round numeric columns
    for col in df_display.columns[1:]:
        if df_display[col].dtype in ["float64", "float32"]:
            df_display[col] = df_display[col].round(2)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df_display.columns),
                    fill_color="steelblue",
                    align="center",
                    font=dict(color="white", size=11),
                ),
                cells=dict(
                    values=[df_display[col] for col in df_display.columns],
                    fill_color="lavender",
                    align="center",
                    font=dict(size=10),
                ),
            )
        ]
    )

    fig.update_layout(
        title="Últimos 12 Meses de Datos",
        height=300 + len(df_display) * 25,
    )

    return fig


def source_registry_table(registry: dict) -> go.Figure:
    """
    Create Plotly table showing data sources for each country.
    """
    rows = []

    for country, sources in registry.items():
        fx_info = sources.get("fx", {})
        ipc_info = sources.get("ipc", {})

        row = {
            "Pa\u00eds": country,
            "Fuente TC": fx_info.get("source", "?"),
            "Serie TC": fx_info.get("series_id", "?"),
            "Fuente IPC": ipc_info.get("source", "?"),
            "Serie IPC": ipc_info.get("series_id", "?"),
        }

        rows.append(row)

    source_df = pd.DataFrame(rows)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(source_df.columns),
                    fill_color="steelblue",
                    align="center",
                    font=dict(color="white", size=11),
                ),
                cells=dict(
                    values=[source_df[col] for col in source_df.columns],
                    fill_color="lavender",
                    align="left",
                    font=dict(size=10),
                ),
            )
        ]
    )

    fig.update_layout(
        title="Registro de Fuentes de Datos",
        height=300 + len(source_df) * 30,
    )

    return fig
