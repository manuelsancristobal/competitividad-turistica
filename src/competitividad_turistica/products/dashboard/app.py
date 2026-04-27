"""Main Streamlit dashboard application for TCRB analysis."""

import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from competitividad_turistica.config.settings import FECHA_INICIO, FECHA_FIN
from competitividad_turistica.config.countries import COUNTRY_CODES, COUNTRY_NAMES, COUNTRIES
from competitividad_turistica.data.pipeline import run_pipeline, cache_status
from competitividad_turistica.calc.tcrb import calculate_tcrb_all
from competitividad_turistica.calc.decomposition import decompose_tcrb
from competitividad_turistica.calc.seasonality import monthly_pattern
from competitividad_turistica.calc.volatility import rolling_volatility, volatility_regime
from competitividad_turistica.calc.correlation import correlation_matrix
from competitividad_turistica.calc.statistics import summary_table, last_n_months
from competitividad_turistica.viz.charts import (
    tcrb_line_chart, tcrb_comparison_chart, decomposition_chart,
    seasonality_chart, volatility_chart, correlation_heatmap,
    rolling_correlation_chart
)
from competitividad_turistica.viz.tables import summary_stats_table, last_12_months_table, source_registry_table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def interpret_tcrb_value(value: float, perspective: str = "receptiva") -> str:
    """
    Interpret TCRB value based on perspective.

    Args:
        value: Current TCRB index value
        perspective: "receptiva" or "emisiva"

    Returns:
        Interpretation string
    """
    if value > 110:
        if perspective == "receptiva":
            return "🔴 Chile muy caro para turistas extranjeros (baja competitividad)"
        else:
            return "🔴 Destino muy caro para chilenos (bajo atractivo)"
    elif value > 100:
        if perspective == "receptiva":
            return "🟡 Chile algo caro para turistas extranjeros (competitividad moderada)"
        else:
            return "🟡 Destino algo caro para chilenos (atractivo moderado)"
    elif value > 90:
        if perspective == "receptiva":
            return "🟢 Chile atractivo para turistas extranjeros (competitividad buena)"
        else:
            return "🟢 Destino accesible para chilenos (atractivo bueno)"
    else:
        if perspective == "receptiva":
            return "🟢 Chile muy atractivo para turistas extranjeros (competitividad excelente)"
        else:
            return "🟢 Destino muy accesible para chilenos (atractivo excelente)"


# Streamlit page configuration
st.set_page_config(
    page_title="TCRB Chile - Dashboard",
    page_icon="TC",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Competitividad Tur\u00edstica de Chile - TCRB Bilateral")
st.markdown(
    "An\u00e1lisis interactivo del Tipo de Cambio Real Bilateral (TCRB) de Chile vs 12 pa\u00edses"
)

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

with st.sidebar:
    st.header("Controles")

    # Data refresh
    if st.button("Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.success("Cache limpiado. Los datos se recargar\u00e1n en la siguiente ejecuci\u00f3n.")

    st.divider()

    # Country selection
    st.subheader("Países")
    all_countries = st.checkbox("Seleccionar todos", value=True)

    if all_countries:
        selected_countries = COUNTRY_CODES
    else:
        selected_countries = st.multiselect(
            "Selecciona países",
            options=COUNTRY_CODES,
            default=["BRA", "PER", "USA"],
            format_func=lambda x: COUNTRY_NAMES[x],
        )

    st.divider()

    # Perspective toggle
    st.subheader("Perspectiva")
    perspective = st.radio(
        "Selecciona perspectiva",
        options=["emisiva", "receptiva"],
        format_func=lambda x: "Chileno viajando al exterior" if x == "emisiva" else "Extranjero visitando Chile",
    )

    st.divider()

    # Date range
    st.subheader("Rango de Fechas")
    date_range = st.slider(
        "Selecciona rango",
        min_value=datetime.strptime(FECHA_INICIO, "%Y-%m-%d"),
        max_value=datetime.today(),
        value=(
            datetime.today() - timedelta(days=365*5),
            datetime.today(),
        ),
        format="YYYY-MM-DD",
    )

    st.divider()

    # Moving average toggle
    show_ma12 = st.checkbox("Mostrar media móvil 12M", value=True)

    # HP Filter option
    show_hp_filter = st.checkbox("Mostrar filtro HP (sin rezago)", value=False)

    st.divider()

    # Argentina FX selector (if applicable)
    if "ARG" in selected_countries or all_countries:
        st.subheader("Argentina - Tipo de Cambio")
        arg_fx_mode = st.radio(
            "Selecciona tipo de cambio",
            options=["oficial", "blue"],
            format_func=lambda x: "Oficial (BCCh/Yahoo)" if x == "oficial" else "Dólar Blue (Bluelytics)",
            horizontal=True,
        )
    else:
        arg_fx_mode = "oficial"

    st.divider()

    # Data quality traffic light (placeholder, filled after data loads)
    st.subheader("Calidad de Datos")
    quality_placeholder = st.empty()

    st.divider()

    # Methodological notes
    with st.expander("📋 Notas Metodológicas"):
        st.markdown("""
        **Base Año 2015=100**
        Todas las series TCRB están normalizadas a 2015=100. Si no hay datos en 2015, se usa 2014-2016.

        **IPC General**
        Se usa IPC general como proxy. Idealmente usaríamos índices turísticos específicos.

        **Volatilidad Anualizada**
        Valores multiplicados por sqrt(12) para representar volatilidad anual.

        **Descomposición Exacta**
        Usa fórmula multiplicativa: TCRB_t/TCRB_{t-12} = (E_t/E_{t-12}) × (P_i_t/P_i_{t-12}) / (P_CL_t/P_CL_{t-12})

        **Correlaciones Significativas**
        Marcadas solo si p < 0.05.

        **Perspectivas**
        - **Receptiva**: Chile como destino (TCRB alto = más caro)
        - **Emisiva**: Chileno viajando (TCRB alto = destino más caro)
        """)

    st.divider()

    # Cache status
    st.subheader("Estado del Cache")
    status = cache_status()
    st.metric("Archivos en cache", status["cached_files"])
    st.metric("Tamaño", f"{status['cache_dir_size_mb']} MB")

# ============================================================================
# LOAD DATA (cached)
# ============================================================================

@st.cache_data(ttl=3600)
def load_data():
    """Load and process all data."""
    try:
        st.info("Descargando datos...")
        df, source_registry = run_pipeline()

        if df is None or df.empty:
            st.error("No se pudieron obtener los datos")
            return None, None, None

        # Calculate TCRB for all countries (now returns tuple with base years)
        df, base_years = calculate_tcrb_all(df, COUNTRY_CODES)

        st.success(f"Datos cargados: {df.shape[0]} filas, {df.index[0].date()} a {df.index[-1].date()}")

        return df, source_registry, base_years

    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        logger.error(e, exc_info=True)
        return None, None, None


# Load data
df, source_registry, base_years = load_data()

if df is None or df.empty:
    st.error("No hay datos disponibles. Verifica la conexión y los parámetros.")
    st.stop()

# Fill data quality placeholder in sidebar
with quality_placeholder.container():
    st.markdown("**Semáforo por país:**")
    quality_colors = {}
    for country in COUNTRY_CODES:
        if f"IPC_{country}" in df.columns:
            ipc_series = df[f"IPC_{country}"].dropna()
            if len(ipc_series) > 0:
                last_date = ipc_series.index[-1]
                days_old = (pd.Timestamp.now() - last_date).days
                if days_old < 30:
                    quality_colors[country] = ("🟢", "Reciente")
                elif days_old < 90:
                    quality_colors[country] = ("🟡", "Moderado")
                else:
                    quality_colors[country] = ("🔴", "Antiguo")
            else:
                quality_colors[country] = ("⚪", "Sin datos")
        else:
            quality_colors[country] = ("⚪", "Sin datos")
    cols = st.columns(3)
    for idx, country in enumerate(COUNTRY_CODES):
        with cols[idx % 3]:
            emoji, status = quality_colors.get(country, ("⚪", "?"))
            st.write(f"{emoji} {COUNTRY_NAMES[country]}: {status}")

# Filter by date range
df_filtered = df.loc[date_range[0]:date_range[1]].copy()

if df_filtered.empty:
    st.error("No hay datos en el rango de fechas seleccionado")
    st.stop()

# Handle Argentina FX mode swap (Official vs Blue)
if arg_fx_mode == "blue" and "ARG" in selected_countries:
    if "TCRB_Idx_ARG_BLUE" in df_filtered.columns:
        # Swap columns so visualization functions use the blue rate
        df_filtered["TCRB_Idx_ARG_OFFICIAL"] = df_filtered["TCRB_Idx_ARG"]
        df_filtered["TCRB_Idx_ARG"] = df_filtered["TCRB_Idx_ARG_BLUE"]
        
        if "TCRB_MA12_ARG_BLUE" in df_filtered.columns:
            df_filtered["TCRB_MA12_ARG_OFFICIAL"] = df_filtered["TCRB_MA12_ARG"]
            df_filtered["TCRB_MA12_ARG"] = df_filtered["TCRB_MA12_ARG_BLUE"]
        
        st.info("💡 Usando Dólar Blue para Argentina")
    else:
        st.warning("⚠️ Datos de Dólar Blue no disponibles. Usando tipo de cambio oficial.")

# ============================================================================
# MAIN NAVIGATION
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Panorama",
    "An\u00e1lisis por Pa\u00eds",
    "Correlaciones",
    "Datos",
])

# ============================================================================
# TAB 1: PANORAMA GENERAL
# ============================================================================

with tab1:
    # Perspective header
    if perspective == "receptiva":
        st.header("🇨🇱 Panorama: Chile Como Destino Turístico")
        st.markdown("*Análisis desde la perspectiva del turista extranjero visitando Chile*")
    else:
        st.header("✈️ Panorama: Chilenos Viajando al Exterior")
        st.markdown("*Análisis desde la perspectiva del chileno viajando al extranjero*")

    # Comparison chart
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("TCRB Multi-País")
        fig_comparison = tcrb_comparison_chart(df_filtered, selected_countries, source_registry)
        st.plotly_chart(fig_comparison, width='stretch')

    with col2:
        st.subheader("Resumen Actual")
        stats_table = summary_table(df_filtered, selected_countries)
        if not stats_table.empty:
            st.dataframe(stats_table, width='stretch', hide_index=True)

        # Perspective interpretation
        st.markdown("**Interpretación:**")
        if perspective == "receptiva":
            st.info("📊 TCRB **bajo** (< 100) = Chile **atractivo** para turistas\n\nTCRB **alto** (> 100) = Chile **caro** para turistas")
        else:
            st.info("📊 TCRB **bajo** (< 100) = Destino **accesible** para chilenos\n\nTCRB **alto** (> 100) = Destino **caro** para chilenos")

    st.divider()

    # Last 12 months
    st.subheader("Últimos 12 Meses")
    last_12 = last_n_months(df_filtered, selected_countries, n=12)
    if not last_12.empty:
        fig_table = last_12_months_table(last_12)
        st.plotly_chart(fig_table, width='stretch')

# ============================================================================
# TAB 2: ANÁLISIS POR PAÍS
# ============================================================================

with tab2:
    st.header("Análisis Profundo por País")

    # Country selector
    selected_country = st.selectbox(
        "Selecciona un país",
        options=selected_countries,
        format_func=lambda x: COUNTRY_NAMES[x],
    )

    if selected_country:
        # Get current TCRB value for interpretation
        tcrb_col = f"TCRB_Idx_{selected_country}"
        if tcrb_col in df_filtered.columns:
            tcrb_series = df_filtered[tcrb_col].dropna()
            if not tcrb_series.empty:
                current_value = tcrb_series.iloc[-1]
                interpretation = interpret_tcrb_value(current_value, perspective)
                st.markdown(f"**Interpretación ({perspective}):  {interpretation}**")

        col1, col2 = st.columns(2)

        # TCRB line chart
        with col1:
            fig_tcrb = tcrb_line_chart(
                df_filtered,
                selected_country,
                show_ma12=show_ma12,
                source_registry=source_registry,
            )
            st.plotly_chart(fig_tcrb, width='stretch')

        # Decomposition
        with col2:
            decomp = decompose_tcrb(df_filtered, selected_country, periods=12)
            if not decomp.empty:
                fig_decomp = decomposition_chart(decomp, selected_country)
                st.plotly_chart(fig_decomp, width='stretch')

        col3, col4 = st.columns(2)

        # Seasonality
        with col3:
            monthly = monthly_pattern(df_filtered[f"TCRB_Idx_{selected_country}"])
            if not monthly.empty:
                fig_seasonal = seasonality_chart(monthly, selected_country)
                st.plotly_chart(fig_seasonal, width='stretch')

        # Volatility
        with col4:
            vol = rolling_volatility(df_filtered[f"TCRB_Idx_{selected_country}"], window=12)
            if not vol.empty and not vol.dropna().empty:
                fig_vol = volatility_chart(df_filtered, vol, selected_country)
                st.plotly_chart(fig_vol, width='stretch')
            else:
                st.info("Datos insuficientes para calcular volatilidad.")

        # Statistics
        st.divider()
        st.subheader("Estadísticas")

        tcrb_idx = df_filtered[f"TCRB_Idx_{selected_country}"].dropna()
        if not tcrb_idx.empty:
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

            with col_stat1:
                st.metric("Valor Actual", f"{tcrb_idx.iloc[-1]:.2f}")

            with col_stat2:
                st.metric("Promedio", f"{tcrb_idx.mean():.2f}")

            with col_stat3:
                st.metric("Mínimo", f"{tcrb_idx.min():.2f}")

            with col_stat4:
                st.metric("Máximo", f"{tcrb_idx.max():.2f}")

# ============================================================================
# TAB 3: CORRELACIONES
# ============================================================================

with tab3:
    st.header("Análisis de Correlaciones")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Matriz de Correlación (p < 0.05)")
        corr, pvalues = correlation_matrix(df_filtered, selected_countries)
        if not corr.empty:
            fig_corr = correlation_heatmap(corr)
            st.plotly_chart(fig_corr, width='stretch')

            # Show p-values summary
            sig_pairs = 0
            for i in range(len(pvalues)):
                for j in range(i+1, len(pvalues)):
                    if pvalues.iloc[i, j] < 0.05:
                        sig_pairs += 1
            total_pairs = (len(pvalues) * (len(pvalues) - 1)) // 2
            st.caption(f"Correlaciones significativas: {sig_pairs} de {total_pairs} pares (p<0.05)")

    with col2:
        st.subheader("Pares de Países")

        if len(selected_countries) >= 2:
            countries_list = [COUNTRY_NAMES[c] for c in selected_countries]
            pair = st.multiselect(
                "Selecciona dos países",
                options=selected_countries,
                max_selections=2,
                format_func=lambda x: COUNTRY_NAMES[x],
                default=selected_countries[:2],
            )

            if len(pair) == 2:
                from competitividad_turistica.calc.correlation import rolling_correlation

                rolling_corr, rolling_pval = rolling_correlation(df_filtered, pair[0], pair[1], window=24)
                if not rolling_corr.empty:
                    fig_rolling = rolling_correlation_chart(rolling_corr, pair[0], pair[1])
                    st.plotly_chart(fig_rolling, width='stretch')

                    # Show current p-value
                    current_pval = rolling_pval.iloc[-1]
                    sig_text = "Significativa" if current_pval < 0.05 else "No significativa"
                    st.caption(f"Correlación actual: p-value = {current_pval:.4f} ({sig_text})")

# ============================================================================
# TAB 4: DATOS
# ============================================================================

with tab4:
    st.header("Datos y Metadatos")

    tab_raw, tab_sources = st.tabs(["Datos Crudos", "Fuentes"])

    with tab_raw:
        st.subheader("DataFrame Completo")

        # Select columns to display
        all_cols = df_filtered.columns.tolist()
        selected_cols = st.multiselect(
            "Selecciona columnas",
            options=all_cols,
            default=all_cols[:10],
        )

        if selected_cols:
            st.dataframe(df_filtered[selected_cols], width='stretch')

            # Download button
            csv = df_filtered[selected_cols].to_csv()
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"TCRB_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    with tab_sources:
        st.subheader("Registro de Fuentes de Datos")

        if source_registry:
            fig_sources = source_registry_table(source_registry)
            st.plotly_chart(fig_sources, width='stretch')

        st.text_area(
            "Detalles de fuentes (JSON)",
            value=str(source_registry),
            height=300,
            disabled=True,
        )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption(
    f"\u00daltima actualizaci\u00f3n: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    f"Datos: {df.index[0].date()} a {df.index[-1].date()}"
)

