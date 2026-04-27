"""TCRB decomposition: exchange rate vs inflation effects."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def decompose_tcrb(df: pd.DataFrame, country: str, periods: int = 12) -> pd.DataFrame:
    """
    Decompose TCRB into two effects using YoY ratios (multiplicative exact formula):
    - Effect cambiario (exchange rate effect)
    - Effect inflación (inflation differential effect)

    Exact formula:
    TCRB_t / TCRB_{t-12} = (E_t / E_{t-12}) × (P_i_t / P_i_{t-12}) / (P_CL_t / P_CL_{t-12})

    For high-inflation countries (e.g., Argentina), also reports interaction term.
    """
    fx_col = f"FX_{country}"
    ipc_col = f"IPC_{country}"
    ipc_chl_col = "IPC_CHL"
    tcrb_col = f"TCRB_Idx_{country}"

    if not all(col in df.columns for col in [fx_col, ipc_col, ipc_chl_col, tcrb_col]):
        logger.warning(f"Missing columns for {country} decomposition")
        return pd.DataFrame()

    # YoY ratios (not percentage changes)
    fx_ratio = df[fx_col] / df[fx_col].shift(periods)
    ipc_ratio = df[ipc_col] / df[ipc_col].shift(periods)
    ipc_chl_ratio = df[ipc_chl_col] / df[ipc_chl_col].shift(periods)
    tcrb_ratio = df[tcrb_col] / df[tcrb_col].shift(periods)

    # Convert ratios to percentage changes
    efecto_cambiario = (fx_ratio - 1) * 100
    efecto_inflacion = ((ipc_ratio / ipc_chl_ratio) - 1) * 100

    # Interaction term (relevant for high-inflation countries like Argentina)
    # Interaction = (fx_ratio - 1) × (ipc_ratio / ipc_chl_ratio - 1)
    interaction_term = (fx_ratio - 1) * ((ipc_ratio / ipc_chl_ratio) - 1) * 100

    # Actual TCRB YoY change (for validation)
    tcrb_yoy = (tcrb_ratio - 1) * 100

    # Build result DataFrame
    result = pd.DataFrame({
        "efecto_cambiario": efecto_cambiario,
        "efecto_inflacion": efecto_inflacion,
        "termino_interaccion": interaction_term,  # Small but reportable for high-inflation countries
        "var_tcrb": tcrb_yoy,
    })

    logger.info(f"TCRB decomposition for {country} (multiplicative, exact formula)")

    return result
