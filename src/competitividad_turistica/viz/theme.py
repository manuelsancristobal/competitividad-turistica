"""Visual theme and styling constants — Light minimal (The Economist/McKinsey style)."""

import plotly.graph_objects as go

from competitividad_turistica.config.countries import COUNTRIES

# === Color palette by region ===
# LATAM: blues
# North America: greys
# Europe: slate
# Asia-Pacific: teal
COLORS = {
    "ARG": "#2563EB",  # Blue 600
    "PER": "#3B82F6",  # Blue 500
    "BOL": "#60A5FA",  # Blue 400
    "BRA": "#1D4ED8",  # Blue 700
    "USA": "#6B7280",  # Grey 500
    "CAN": "#9CA3AF",  # Grey 400
    "ESP": "#475569",  # Slate 600
    "FRA": "#64748B",  # Slate 500
    "DEU": "#334155",  # Slate 700
    "GBR": "#94A3B8",  # Slate 400
    "CHN": "#0D9488",  # Teal 600
    "AUS": "#14B8A6",  # Teal 500
}

# Accent colors
ACCENT_DARK = "#1E293B"  # Slate 800 — titles, key elements
ACCENT_MID = "#64748B"  # Slate 500 — secondary text
ACCENT_LIGHT = "#F8FAFC"  # Slate 50 — backgrounds
BASELINE_COLOR = "#CBD5E1"  # Slate 300 — base line at 100

# Typography
FONT_FAMILY = "Inter, Helvetica Neue, Helvetica, Arial, sans-serif"
FONT_SIZE_TITLE = 20
FONT_SIZE_SUBTITLE = 14
FONT_SIZE_LABEL = 12
FONT_SIZE_ANNOTATION = 10

# Month labels in Spanish
MONTH_LABELS_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# Default Plotly layout settings — minimal editorial style
LAYOUT_DEFAULTS = dict(
    font=dict(family=FONT_FAMILY, size=FONT_SIZE_LABEL, color=ACCENT_DARK),
    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=11),
    ),
    margin=dict(l=60, r=40, t=80, b=80),
    xaxis=dict(showgrid=False, zeroline=False, linecolor="#E2E8F0", linewidth=1),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="#EEEEEE", zeroline=False, linecolor="#E2E8F0", linewidth=1),
)


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
        fig.update_layout(
            title=dict(
                text=title,
                x=0,
                xanchor="left",
                font=dict(size=FONT_SIZE_TITLE, color=ACCENT_DARK, family=FONT_FAMILY),
            )
        )

    if subtitle:
        fig.add_annotation(
            text=subtitle,
            x=0,
            y=1.06,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=FONT_SIZE_SUBTITLE, color=ACCENT_MID),
            xanchor="left",
            yanchor="top",
        )

    return fig


def add_footnote(fig: go.Figure, text: str) -> go.Figure:
    """Add a discrete source footnote at the bottom of the figure."""
    fig.add_annotation(
        text=text,
        x=0,
        y=-0.12,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=9, color=ACCENT_MID, family=FONT_FAMILY),
        xanchor="left",
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

    return f"Fuente: TC: {fx_text} | IPC: {ipc_text}"
