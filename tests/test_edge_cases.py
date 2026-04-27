import numpy as np
import pandas as pd
import pytest

from competitividad_turistica.calc.tcrb import calculate_tcrb_raw, normalize_index
from competitividad_turistica.data.sources.fred import _inflation_rate_to_cpi_index


def test_tcrb_division_by_zero():
    """Caso Borde: IPC de Chile es cero (teóricamente imposible, pero el código debe ser robusto)."""
    dates = pd.date_range("2020-01-01", periods=3, freq="MS")
    fx = pd.Series([100.0, 100.0, 100.0], index=dates)
    ipc_foreign = pd.Series([110.0, 110.0, 110.0], index=dates)
    ipc_chile = pd.Series([0.0, 110.0, 110.0], index=dates) # Cero en la primera posición

    tcrb = calculate_tcrb_raw(fx, ipc_foreign, ipc_chile)

    # Debería dar inf en el primer elemento
    assert np.isinf(tcrb.iloc[0])
    assert tcrb.iloc[1] == 100.0

def test_tcrb_mismatched_dates():
    """Caso Borde: No hay intersección de fechas entre series."""
    dates_1 = pd.date_range("2020-01-01", periods=3, freq="MS")
    dates_2 = pd.date_range("2021-01-01", periods=3, freq="MS")

    fx = pd.Series([800.0, 810.0, 820.0], index=dates_1)
    ipc_foreign = pd.Series([110.0, 112.0, 114.0], index=dates_2)
    ipc_chile = pd.Series([120.0, 122.0, 125.0], index=dates_1)

    tcrb = calculate_tcrb_raw(fx, ipc_foreign, ipc_chile)

    # El resultado debe ser una serie vacía, no crashear
    assert tcrb.empty

def test_normalize_no_data_in_base_year():
    """Caso Borde: Se pide un año base (2015) pero solo hay datos recientes."""
    dates = pd.date_range("2024-01-01", periods=12, freq="MS")
    series = pd.Series(np.linspace(100, 110, 12), index=dates)

    # El código debe usar el primer año disponible (2024) como fallback
    normalized, effective_year = normalize_index(series, base_year=2015, base=100.0)

    assert effective_year == 2024
    assert pytest.approx(normalized.mean(), 0.01) == 100.0

def test_normalize_with_all_nans():
    """Caso Borde: Serie compuesta solo por NaNs."""
    dates = pd.date_range("2020-01-01", periods=12, freq="MS")
    series = pd.Series([np.nan] * 12, index=dates)

    normalized, effective_year = normalize_index(series, base_year=2015)

    # Debe retornar la serie original (con NaNs) y None como año efectivo
    assert normalized.isna().all()
    assert effective_year is None

def test_extreme_inflation_conversion():
    """Caso Borde: Inflación masiva (tipo Argentina/Zimbabue) de 1000% anual."""
    dates = pd.date_range("2020-01-01", periods=1, freq="YS")
    inflation_rate = pd.Series([1000.0], index=dates) # 1000%

    cpi = _inflation_rate_to_cpi_index(inflation_rate, base=100.0)

    # Al final del año (mes 12), el índice debería ser 1100 (100 base + 1000% aumento)
    # Nota: El loop interno llega hasta el mes 12.
    # El valor final después de 12 meses de capitalización mensual de (1+10)^(1/12)
    assert pytest.approx(cpi.iloc[-1], 0.1) == 100 * (1 + 1000/100)**(11/12)

