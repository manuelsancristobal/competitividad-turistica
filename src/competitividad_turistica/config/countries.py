"""Configuration for 12 countries in TCRB analysis."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class CountryConfig:
    """Configuration for a country in TCRB analysis."""
    name: str                           # Display name
    code: str                           # ISO 3166-1 alpha-3
    currency: str                       # ISO 4217
    fx_ticker_direct: Optional[str]     # Yahoo ticker for MON/CLP
    fx_ticker_cross: Optional[tuple]    # (MON/USD, USD/CLP) for cross-rate
    ipc_fred_series: list               # FRED CPI series IDs (ordered by preference)
    ipc_wb_country: str                 # World Bank country code
    ipc_fred_inflation_annual: Optional[str]  # FRED annual inflation for synthetic CPI
    bcch_fx_series: Optional[str]       # BCCh FX series ID
    bcch_ipc_series: Optional[str]      # BCCh CPI series ID
    color_primary: str                  # HEX color for charts
    color_secondary: str                # Secondary color
    region: str                         # "latam" | "northamerica" | "europe" | "asiapacific"
    uses_eur: bool = False              # True for Spain, France, Germany
    indec_ipc_series: Optional[str] = None  # INDEC IPC series (Argentina only)
    use_worldbank_primary: bool = False     # If True, try World Bank before FRED
    has_parallel_fx: bool = False           # If True, has parallel/blue market FX (Argentina)
    tourist_weight: float = 1.0             # Tourist flow weight (1.0 = equal weight)


COUNTRIES = {
    "ARG": CountryConfig(
        name="Argentina",
        code="ARG",
        currency="ARS",
        fx_ticker_direct=None,
        fx_ticker_cross=("ARSUSD=X", "CLP=X"),
        ipc_fred_series=["DDOE01ARA086NWDB", "FPCPITOTLZGARG"],
        ipc_wb_country="ARG",
        ipc_fred_inflation_annual="FPCPITOTLZGARG",
        bcch_fx_series="F072.CLP.ARS.N.O.D",
        bcch_ipc_series=None,
        color_primary="#1f77b4",
        color_secondary="#aec7e8",
        region="latam",
        indec_ipc_series="148.3_INACVH_DICI_M_19",
        has_parallel_fx=True,
    ),
    "PER": CountryConfig(
        name="Perú",
        code="PER",
        currency="PEN",
        fx_ticker_direct=None,
        fx_ticker_cross=("PENUSD=X", "CLP=X"),
        ipc_fred_series=["DDOE01PEA086NWDB", "FPCPITOTLZGPER"],
        ipc_wb_country="PER",
        ipc_fred_inflation_annual="FPCPITOTLZGPER",
        bcch_fx_series="F072.CLP.PEN.N.O.D",
        bcch_ipc_series=None,
        color_primary="#ff7f0e",
        color_secondary="#ffbb78",
        region="latam",
        use_worldbank_primary=True,
    ),
    "BOL": CountryConfig(
        name="Bolivia",
        code="BOL",
        currency="BOB",
        fx_ticker_direct=None,
        fx_ticker_cross=("BOBUSD=X", "CLP=X"),
        ipc_fred_series=["DDOE01BOA086NWDB", "FPCPITOTLZGBOL"],
        ipc_wb_country="BOL",
        ipc_fred_inflation_annual=None,
        bcch_fx_series=None,
        bcch_ipc_series=None,
        color_primary="#2ca02c",
        color_secondary="#98df8a",
        region="latam",
        use_worldbank_primary=True,
    ),
    "BRA": CountryConfig(
        name="Brasil",
        code="BRA",
        currency="BRL",
        fx_ticker_direct=None,
        fx_ticker_cross=("BRLUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01BRM657N", "FPCPITOTLZGBRA"],
        ipc_wb_country="BRA",
        ipc_fred_inflation_annual="FPCPITOTLZGBRA",
        bcch_fx_series="F072.CLP.BRL.N.O.D",
        bcch_ipc_series=None,
        color_primary="#d62728",
        color_secondary="#ff9896",
        region="latam",
    ),
    "USA": CountryConfig(
        name="Estados Unidos",
        code="USA",
        currency="USD",
        fx_ticker_direct="CLP=X",  # CLP per USD (already in correct direction)
        fx_ticker_cross=None,
        ipc_fred_series=["CPIAUCSL"],  # USA CPI uses different naming convention
        ipc_wb_country="USA",
        ipc_fred_inflation_annual="FPCPITOTLZGUSA",
        bcch_fx_series="F073.TCO.PRE.Z.D",  # Dólar Observado
        bcch_ipc_series=None,
        color_primary="#9467bd",
        color_secondary="#c5b0d5",
        region="northamerica",
    ),
    "CAN": CountryConfig(
        name="Canadá",
        code="CAN",
        currency="CAD",
        fx_ticker_direct=None,
        fx_ticker_cross=("CADUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01CAM661N", "FPCPITOTLZGCAN"],
        ipc_wb_country="CAN",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.CAD.N.O.D",
        bcch_ipc_series=None,
        color_primary="#8c564b",
        color_secondary="#c7c7c7",
        region="northamerica",
    ),
    "ESP": CountryConfig(
        name="España",
        code="ESP",
        currency="EUR",
        fx_ticker_direct=None,
        fx_ticker_cross=("EURUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01ESM661N", "FPCPITOTLZGESP"],
        ipc_wb_country="ESP",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.EUR.N.O.D",
        bcch_ipc_series=None,
        color_primary="#e377c2",
        color_secondary="#f7b6d2",
        region="europe",
        uses_eur=True,
    ),
    "FRA": CountryConfig(
        name="Francia",
        code="FRA",
        currency="EUR",
        fx_ticker_direct=None,
        fx_ticker_cross=("EURUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01FRM661N", "FPCPITOTLZGFRA"],
        ipc_wb_country="FRA",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.EUR.N.O.D",
        bcch_ipc_series=None,
        color_primary="#7f7f7f",
        color_secondary="#c7c7c7",
        region="europe",
        uses_eur=True,
    ),
    "DEU": CountryConfig(
        name="Alemania",
        code="DEU",
        currency="EUR",
        fx_ticker_direct=None,
        fx_ticker_cross=("EURUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01DEM661N", "FPCPITOTLZGDEU"],
        ipc_wb_country="DEU",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.EUR.N.O.D",
        bcch_ipc_series=None,
        color_primary="#bcbd22",
        color_secondary="#dbdb8d",
        region="europe",
        uses_eur=True,
    ),
    "GBR": CountryConfig(
        name="Reino Unido",
        code="GBR",
        currency="GBP",
        fx_ticker_direct=None,
        fx_ticker_cross=("GBPUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01GBM659N", "FPCPITOTLZGGBR"],
        ipc_wb_country="GBR",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.GBP.N.O.D",
        bcch_ipc_series=None,
        color_primary="#17becf",
        color_secondary="#9edae5",
        region="europe",
    ),
    "CHN": CountryConfig(
        name="China",
        code="CHN",
        currency="CNY",
        fx_ticker_direct=None,
        fx_ticker_cross=("CNYUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01CNM659N", "FPCPITOTLZGCHN"],
        ipc_wb_country="CHN",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.CNY.N.O.D",
        bcch_ipc_series=None,
        color_primary="#ff9896",
        color_secondary="#ffbb78",
        region="asiapacific",
    ),
    "AUS": CountryConfig(
        name="Australia",
        code="AUS",
        currency="AUD",
        fx_ticker_direct=None,
        fx_ticker_cross=("AUDUSD=X", "CLP=X"),
        ipc_fred_series=["CPALTT01AUM661N", "FPCPITOTLZGAUS"],
        ipc_wb_country="AUS",
        ipc_fred_inflation_annual=None,
        bcch_fx_series="F072.CLP.AUD.N.O.D",
        bcch_ipc_series=None,
        color_primary="#c7c7c7",
        color_secondary="#f7b6d2",
        region="asiapacific",
    ),
}

# Chile IPC configuration
CHILE_IPC_FRED = ["CPALTT01CLM661N", "FPCPITOTLZGCHL"]
CHILE_BCCH_IPC = "F074.IPC.IND.Z.EP09.C.M"
CHILE_WB_CODE = "CHL"

# EUR countries share exchange rate
EUR_COUNTRIES = ["ESP", "FRA", "DEU"]
EUR_TICKER_CROSS = ("EURUSD=X", "CLP=X")

# Country lists by region
COUNTRIES_LATAM = ["ARG", "PER", "BOL", "BRA"]
COUNTRIES_NORTHAMERICA = ["USA", "CAN"]
COUNTRIES_EUROPE = ["ESP", "FRA", "DEU", "GBR"]
COUNTRIES_ASIAPACIFIC = ["CHN", "AUS"]

COUNTRY_CODES = list(COUNTRIES.keys())
COUNTRY_NAMES = {code: config.name for code, config in COUNTRIES.items()}
