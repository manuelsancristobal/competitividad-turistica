"""Streamlit dashboard — Competitividad Turística de Chile (minimal edition)."""

import logging
from datetime import datetime, timedelta

import streamlit as st

from competitividad_turistica.calc.correlation import correlation_matrix
from competitividad_turistica.calc.decomposition import decompose_tcrb
from competitividad_turistica.calc.tcrb import calculate_tcrb_all
from competitividad_turistica.config.countries import COUNTRY_CODES, COUNTRY_NAMES
from competitividad_turistica.config.settings import FECHA_INICIO
from competitividad_turistica.data.pipeline import run_pipeline
from competitividad_turistica.viz.charts import (
    correlation_heatmap,
    decomposition_chart,
    tcrb_comparison_chart,
    tcrb_line_chart,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Page config ===
st.set_page_config(
    page_title="Competitividad Turística — Chile",
    page_icon="TC",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === Inject minimal CSS ===
st.markdown(
    """
    <style>
    /* Hide Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px;}

    /* White background, editorial feel */
    .stApp {background-color: #FFFFFF;}
    [data-testid="stSidebar"] {background-color: #FAFAFA; border-right: 1px solid #F1F5F9;}
    [data-testid="stSidebar"] .block-container {padding-top: 2rem;}

    /* Tabs: thin underline style */
    .stTabs [data-baseweb="tab-list"] {gap: 2rem; border-bottom: 1px solid #E2E8F0;}
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem; font-weight: 500; color: #64748B;
        padding: 0.5rem 0; border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {color: #1E293B; border-bottom-color: #1E293B;}

    /* Typography */
    h1, h2, h3 {font-family: 'Inter', 'Helvetica Neue', sans-serif; font-weight: 600; color: #1E293B;}
    h1 {font-size: 1.75rem !important; margin-bottom: 0.25rem !important;}
    p, .stMarkdown {font-family: 'Inter', 'Helvetica Neue', sans-serif; color: #334155;}
    .stCaption, caption {color: #94A3B8; font-size: 0.8rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# === Sidebar (3 controls) ===
with st.sidebar:
    st.markdown("### Configuración")

    # 1. Country selector
    all_countries = st.checkbox("Todos los países", value=True)
    if all_countries:
        selected_countries = COUNTRY_CODES
    else:
        selected_countries = st.multiselect(
            "Países",
            options=COUNTRY_CODES,
            default=["BRA", "PER", "USA"],
            format_func=lambda x: COUNTRY_NAMES[x],
        )

    st.markdown("---")

    # 2. Perspective toggle
    perspective = st.radio(
        "Perspectiva",
        options=["receptiva", "emisiva"],
        format_func=lambda x: (
            "Receptiva (turista visitando Chile)" if x == "receptiva" else "Emisiva (chileno viajando)"
        ),
        horizontal=True,
    )

    st.markdown("---")

    # 3. Date range
    date_range = st.slider(
        "Período",
        min_value=datetime.strptime(FECHA_INICIO, "%Y-%m-%d"),
        max_value=datetime.today(),
        value=(datetime.today() - timedelta(days=365 * 5), datetime.today()),
        format="YYYY-MM",
    )


# === Load data ===
@st.cache_data(ttl=3600)
def load_data():
    """Load and process all data."""
    try:
        df, source_registry = run_pipeline()
        if df is None or df.empty:
            return None, None
        df, _base_years = calculate_tcrb_all(df, COUNTRY_CODES)
        return df, source_registry
    except Exception as e:
        logger.error(e, exc_info=True)
        return None, None


df, source_registry = load_data()

if df is None or df.empty:
    st.error("No hay datos disponibles. Verifica la conexión.")
    st.stop()

# Filter by date
df_filtered = df.loc[date_range[0] : date_range[1]].copy()

if df_filtered.empty:
    st.error("No hay datos en el rango seleccionado.")
    st.stop()

# === Title ===
st.markdown("# Competitividad Turística de Chile")
perspective_label = "Receptiva — Chile como destino" if perspective == "receptiva" else "Emisiva — Chileno viajando"
st.caption(perspective_label)

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["Panorama", "Análisis por País", "Correlaciones"])

# --- Tab 1: Panorama ---
with tab1:
    fig_comparison = tcrb_comparison_chart(df_filtered, selected_countries, source_registry)
    st.plotly_chart(fig_comparison, use_container_width=True)

# --- Tab 2: Análisis por País ---
with tab2:
    selected_country = st.selectbox(
        "País",
        options=selected_countries,
        format_func=lambda x: COUNTRY_NAMES[x],
    )

    if selected_country:
        col1, col2 = st.columns(2)

        with col1:
            fig_tcrb = tcrb_line_chart(
                df_filtered,
                selected_country,
                show_ma12=True,
                source_registry=source_registry,
            )
            st.plotly_chart(fig_tcrb, use_container_width=True)

        with col2:
            decomp = decompose_tcrb(df_filtered, selected_country, periods=12)
            if not decomp.empty:
                fig_decomp = decomposition_chart(decomp, selected_country)
                st.plotly_chart(fig_decomp, use_container_width=True)

# --- Tab 3: Correlaciones ---
with tab3:
    corr, _pvalues = correlation_matrix(df_filtered, selected_countries)
    if not corr.empty:
        fig_corr = correlation_heatmap(corr)
        st.plotly_chart(fig_corr, use_container_width=True)

# === Footer ===
st.caption(
    f"Datos: {df.index[0].strftime('%Y-%m')} — {df.index[-1].strftime('%Y-%m')} | Actualizado: {datetime.now().strftime('%Y-%m-%d')}"
)
