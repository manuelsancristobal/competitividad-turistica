"""Data pipeline orchestrator - handles cascade of data sources."""

import json
import logging
from datetime import datetime

import pandas as pd

from competitividad_turistica.config.countries import (
    CHILE_WB_CODE,
    COUNTRIES,
    COUNTRY_CODES,
    EUR_COUNTRIES,
)
from competitividad_turistica.config.settings import FECHA_FIN, FECHA_INICIO, PROJECT_ROOT

from .cache import clear_cache
from .models import DataResult
from .sources import bcch, bluelytics, fred, indec, worldbank, yahoo

logger = logging.getLogger(__name__)


def fetch_country_fx(country_code: str, start: str, end: str) -> DataResult:
    """
    Fetch FX for a country using cascade: BCCh → Yahoo (direct/cross) → fail.
    """
    config = COUNTRIES[country_code]

    # Try BCCh first if credentials available and series configured
    if bcch.is_available() and config.bcch_fx_series:
        result = bcch.fetch_fx(config.bcch_fx_series, start, end, country_code)
        if result.success:
            return result

    # Try Yahoo Finance (direct or cross-rate)
    result = yahoo.fetch_fx(country_code, config.fx_ticker_direct, config.fx_ticker_cross, start, end)

    return result


def fetch_country_ipc(country_code: str, start: str, end: str) -> DataResult:
    """
    Fetch IPC for a country using cascade:
    - BCCh (if available)
    - For ARG: INDEC (2017-present) → FRED (historical) → World Bank
    - For BOL/PER: World Bank (primary) → FRED → World Bank
    - For others: FRED → World Bank
    """
    config = COUNTRIES[country_code]

    # Try BCCh first if credentials available and series configured
    if bcch.is_available() and config.bcch_ipc_series:
        result = bcch.fetch_ipc(config.bcch_ipc_series, start, end, country_code)
        if result.success:
            return result

    # Argentina: Try INDEC first (covers 2017-present)
    if country_code == "ARG" and config.indec_ipc_series:
        result = indec.fetch_ipc_indec(start, end)
        if result.success:
            return result
        logger.info(f"INDEC fetch failed for {country_code}, trying FRED...")

    # For BOL/PER: Try World Bank first (more recent data than FRED)
    if config.use_worldbank_primary:
        result = worldbank.fetch_ipc_worldbank(config.ipc_wb_country, start, end)
        if result.success:
            return result
        logger.info(f"World Bank fetch failed for {country_code}, trying FRED...")

    # Try FRED
    result = fred.fetch_ipc_fred(config.ipc_fred_series, start, end, country_code)
    if result.success:
        return result

    # Try World Bank (fallback if not already tried)
    if not config.use_worldbank_primary:
        result = worldbank.fetch_ipc_worldbank(config.ipc_wb_country, start, end)
        if result.success:
            return result

    # All failed
    logger.error(f"Could not fetch IPC for {country_code} from any source")
    return DataResult(
        data=None,
        source="unknown",
        series_id="unknown",
        country=country_code,
        variable="ipc",
        coverage=("", ""),
        obs_count=0,
        success=False,
        error_message="All IPC sources exhausted",
    )


def fetch_chile_ipc(start: str, end: str) -> DataResult:
    """Fetch Chile's IPC specifically."""
    # Try BCCh first
    if bcch.is_available():
        from competitividad_turistica.config.countries import CHILE_BCCH_IPC

        result = bcch.fetch_ipc(CHILE_BCCH_IPC, start, end, "CHL")
        if result.success:
            return result

    # Try FRED
    result = fred.fetch_ipc_chile(start, end)
    if result.success:
        return result

    # Try World Bank
    result = worldbank.fetch_ipc_worldbank(CHILE_WB_CODE, start, end)

    return result


def fetch_all_countries(start: str = FECHA_INICIO, end: str = FECHA_FIN) -> dict[str, tuple[DataResult, DataResult]]:
    """
    Fetch FX and IPC for all 12 countries.
    Returns dict: {country_code: (fx_result, ipc_result)}
    """
    logger.info(f"Fetching data for all countries ({start} to {end})")

    results = {}

    # Optimization: EUR countries share the same exchange rate
    eur_fx_result = None

    for country_code in COUNTRY_CODES:
        logger.info(f"Fetching {country_code}...")

        # FX
        if country_code in EUR_COUNTRIES and eur_fx_result is not None:
            # Reuse EUR result
            fx_result = DataResult(
                data=eur_fx_result.data.copy(),
                source=eur_fx_result.source,
                series_id=eur_fx_result.series_id,
                country=country_code,
                variable="fx",
                coverage=eur_fx_result.coverage,
                obs_count=eur_fx_result.obs_count,
                success=eur_fx_result.success,
            )
        else:
            fx_result = fetch_country_fx(country_code, start, end)

            # Cache EUR result for reuse
            if country_code in EUR_COUNTRIES and fx_result.success and eur_fx_result is None:
                eur_fx_result = fx_result

        # IPC
        ipc_result = fetch_country_ipc(country_code, start, end)

        results[country_code] = (fx_result, ipc_result)

        if fx_result.success and ipc_result.success:
            logger.info(f"OK {country_code}: FX from {fx_result.source}, IPC from {ipc_result.source}")
        else:
            status = f"FX: {'OK' if fx_result.success else 'FAIL'}, IPC: {'OK' if ipc_result.success else 'FAIL'}"
            logger.warning(f"FAIL {country_code}: {status}")

    return results


def fetch_parallel_fx_optional(country_code: str, start: str, end: str) -> DataResult:
    """
    Fetch parallel/informal market exchange rate for countries that have it.
    Currently only Argentina (dólar blue).
    Returns DataResult or None if not available.
    """
    if country_code == "ARG":
        result = bluelytics.fetch_fx_bluelytics(start, end)
        if result.success:
            logger.info("Fetched ARG blue dollar (parallel market)")
            return result
        else:
            logger.warning(f"Failed to fetch ARG blue dollar: {result.error_message}")
            return None
    return None


def build_dataframe(
    results: dict[str, tuple[DataResult, DataResult]], chile_ipc: DataResult, parallel_fx: dict[str, DataResult] = None
) -> tuple[pd.DataFrame, dict]:
    """
    Build consolidated DataFrame from all results.
    Includes optional parallel FX rates (e.g., Argentina blue dollar).
    Returns (df, source_registry).
    """
    logger.info("Building consolidated DataFrame...")

    if parallel_fx is None:
        parallel_fx = {}

    df_dict = {}

    # Add Chile IPC
    if chile_ipc.success:
        df_dict["IPC_CHL"] = chile_ipc.data
    else:
        logger.error("Chile IPC failed - cannot proceed")
        return None, {}

    # Add country data
    source_registry = {}

    for country_code, (fx_result, ipc_result) in results.items():
        if not fx_result.success or not ipc_result.success:
            logger.warning(f"Skipping {country_code}: incomplete data")
            continue

        df_dict[f"FX_{country_code}"] = fx_result.data
        df_dict[f"IPC_{country_code}"] = ipc_result.data

        # Track sources
        source_registry[country_code] = {
            "fx": {
                "source": fx_result.source,
                "series_id": fx_result.series_id,
            },
            "ipc": {
                "source": ipc_result.source,
                "series_id": ipc_result.series_id,
            },
        }

        # Add parallel FX if available
        if country_code in parallel_fx and parallel_fx[country_code] is not None:
            fx_blue_raw = parallel_fx[country_code].data

            # Convert ARS/USD (blue) to CLP/ARS: (CLP/USD) / (ARS/USD)
            if country_code == "ARG" and "FX_USA" in df_dict:
                fx_usd_clp = df_dict["FX_USA"]
                # Align dates
                common = fx_usd_clp.index.intersection(fx_blue_raw.index)
                fx_blue_converted = fx_usd_clp.loc[common] / fx_blue_raw.loc[common]

                df_dict[f"FX_{country_code}_BLUE"] = fx_blue_converted
                source_registry[country_code]["fx_parallel"] = {
                    "source": parallel_fx[country_code].source,
                    "series_id": parallel_fx[country_code].series_id,
                    "note": "Converted to CLP/ARS using official USD/CLP",
                }
                logger.info(f"Added converted parallel FX for {country_code}")
            else:
                df_dict[f"FX_{country_code}_BLUE"] = fx_blue_raw
                source_registry[country_code]["fx_parallel"] = {
                    "source": parallel_fx[country_code].source,
                    "series_id": parallel_fx[country_code].series_id,
                }

    # Combine into DataFrame
    df = pd.DataFrame(df_dict)

    # Ensure master monthly index (MS) to avoid alignment issues
    if not df.empty:
        start_date = df.index.min()
        end_date = df.index.max()
        master_index = pd.date_range(start=start_date, end=end_date, freq="MS")
        df = df.reindex(master_index)

        # Final interpolation for very small gaps if any (max 2 months)
        df = df.interpolate(method="linear", limit=2)

    # Align dates - keep intersection of all series
    df = df.dropna(how="all", axis=0)

    logger.info(f"Consolidated DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")
    logger.info(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
    logger.info(f"Coverage: {len(source_registry)} complete countries")

    return df, source_registry


def _export_consolidated_data(df: pd.DataFrame, source_registry: dict) -> None:
    """
    Export consolidated DataFrame and source registry to output directory.
    Called at the end of Extract layer (after build_dataframe).
    """
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export consolidated DataFrame
    csv_path = output_dir / "datos_consolidados.csv"
    df.to_csv(csv_path)
    logger.info(f"Exported consolidated data to {csv_path}")

    # Export source registry with metadata
    json_path = output_dir / "fuentes_datos.json"
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "rows": len(df),
        "columns": list(df.columns),
        "date_range": (str(df.index[0])[:10], str(df.index[-1])[:10]),
        "sources": source_registry,
    }
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Exported source registry to {json_path}")


def run_pipeline(start: str = FECHA_INICIO, end: str = FECHA_FIN) -> tuple[pd.DataFrame, dict]:
    """
    Execute full pipeline: fetch all data, build DataFrame.
    Returns (df, source_registry).

    Also exports consolidated data to CSV and source registry to JSON.
    """
    logger.info("=" * 60)
    logger.info("TCRB DATA PIPELINE START")
    logger.info("=" * 60)

    # Fetch all countries
    results = fetch_all_countries(start, end)

    # Fetch Chile IPC separately
    chile_ipc = fetch_chile_ipc(start, end)

    # Fetch optional parallel FX rates (e.g., Argentina blue dollar)
    parallel_fx = {}
    for country_code in COUNTRY_CODES:
        config = COUNTRIES[country_code]
        if config.has_parallel_fx:
            parallel_fx[country_code] = fetch_parallel_fx_optional(country_code, start, end)

    # Build DataFrame
    df, source_registry = build_dataframe(results, chile_ipc, parallel_fx)

    # Export consolidated data to CSV and source registry to JSON
    if df is not None:
        _export_consolidated_data(df, source_registry)

    logger.info("=" * 60)
    logger.info("TCRB DATA PIPELINE END")
    logger.info("=" * 60)

    return df, source_registry


def refresh_cache():
    """Clear and re-run pipeline."""
    logger.info("Refreshing cache...")
    clear_cache()
    return run_pipeline()
