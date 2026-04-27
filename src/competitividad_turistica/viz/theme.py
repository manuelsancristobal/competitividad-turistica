"""Visual theme and styling constants."""

import plotly.graph_objects as go
from competitividad_turistica.config.countries import COUNTRIES

# Color palette for 12 countries (region-aware)
COLORS = {
    "ARG": "#1f77b4",    # Blue
    "PER": "#ff7f0e",    # Orange
    "BOL": "#2ca02c",    # Green
    "BRA": "#d62728",    # Red
    "USA": "#9467bd",    # Purple
    "CAN": "#8c564b",    # Brown
    "ESP": "#e377c2",    # Pink
    "FRA": "#7f7f7f",    # Grey
    "DEU": "#bcbd22",    # Yellow-green
    "GBR": "#17becf",    # Cyan
    "CHN": "#ff9896",    # Light red
    "AUS": "#c5b0d5",    # Light purple
}

# Typography
FONT_FAMILY = "Segoe UI, Roboto, sans-serif"
FONT_SIZE_TITLE = 18
FONT_SIZE_SUBTITLE = 14
FONT_SIZE_LABEL = 12
FONT_SIZE_ANNOTATION = 10

# BCCh-inspired colors
BCH_BLUE = "#003b71"
BCH_GREY = "#f0f0f0"
BCH_TEXT = "#333333"

# Default Plotly layout settings
LAYOUT_DEFAULTS = dict(
    font=dict(family=FONT_FAMILY, size=FONT_SIZE_LABEL, color=BCH_TEXT),
    plot_bgcolor=BCH_GREY,
    paper_bgcolor="white",
    hovermode="x unified",
    showlegend=True,
    legend=dict(x=0, y=1, bgcolor="rgba(255,255,255,0.8)", bordercolor=BCH_TEXT, borderwidth=1),
    margin=dict(l=60, r=20, t=60, b=60),
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor="white"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="white"),
)

# Month labels in Spanish
MONTH_LABELS_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                   "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def get_country_color(country_code: str) -> str:
    """Get color for a country."""
    return COLORS.get(country_code, "#cccccc")


def get_country_name(country_code: str) -> str:
    """Get display name for a country."""
    if country_code in COUNTRIES:
        return COUNTRIES[country_code].name
    return country_code


def apply_theme(fig: go.Figure, title: str = "", subtitle: str = "") -> go.Figure:
    """Apply standard theme to a Plotly figure."""
    fig.update_layout(**LAYOUT_DEFAULTS)

    if title:
        fig.add_annotation(
            text=title,
            x=0.5,
            y=1.08,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=FONT_SIZE_TITLE, color=BCH_BLUE),
            xanchor="center",
            yanchor="top",
        )

    if subtitle:
        fig.add_annotation(
            text=subtitle,
            x=0.5,
            y=1.03,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=FONT_SIZE_SUBTITLE, color=BCH_TEXT),
            xanchor="center",
            yanchor="top",
        )

    return fig


def source_footnote(sources: dict, country: str = "") -> str:
    """
    Generate footnote text with source attribution.
    sources dict: {"fx": {"source": "...", "series_id": "..."}, "ipc": {...}}
    """
    if country not in sources:
        return "Fuente: No especificada"

    src = sources[country]
    fx_src = src.get("fx", {})
    ipc_src = src.get("ipc", {})

    fx_text = f"{fx_src.get('source', '?')} ({fx_src.get('series_id', '?')})"
    ipc_text = f"{ipc_src.get('source', '?')} ({ipc_src.get('series_id', '?')})"

    return f"Fuente: Tipo de cambio: {fx_text} | IPC: {ipc_text}"

