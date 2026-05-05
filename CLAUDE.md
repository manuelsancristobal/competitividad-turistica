# CLAUDE.md — competitividad-turistica

## Quick Commands
```bash
make install-dev    # Install project + dev deps
make lint           # Ruff check + format
make test           # pytest -v
make coverage       # pytest + HTML + XML coverage
make assets         # Run data pipeline
make ver            # Launch Streamlit dashboard
python run.py all   # Pipeline + deploy
```

## Architecture
```
src/competitividad_turistica/
├── calc/           # Pure calculation modules (tcrb, correlation, volatility, statistics, decomposition, seasonality)
├── config/         # Settings (pydantic-settings), countries config
├── data/           # Pipeline, cache, downloaders (bcch, fred, yahoo, worldbank)
├── products/       # Dashboard (Streamlit app)
└── viz/            # Plotly chart builders, theme, tables
```

- Entry point: `run.py` (CLI: assets, deploy, ver, all)
- Data cached in `data/external/` as CSV + JSON metadata
- Settings loaded from `.env` via pydantic-settings

## Testing
- Framework: pytest + pytest-cov
- Run: `pytest tests/ -v`
- Coverage reports: term-missing + XML (for CI/Codecov)
- Fixtures in `tests/conftest.py`

## Code Style
- Linter/formatter: ruff (line-length=120, target py310)
- Rules: E, F, W, I, UP, B, SIM (ignore E501)
- isort: first-party = competitividad_turistica
- Pre-commit: ruff + ruff-format + nbstripout + trailing-whitespace + end-of-file-fixer

## Key Patterns
- TCRB index normalized to base year 2015=100
- All calc modules are pure functions (DataFrame/Series in → DataFrame/Series out)
- Cache uses CSV + JSON metadata (CacheEntry dataclass)
- Dashboard imports from calc/, config/, data/, viz/ — never writes data
- Dependencies use flexible ranges (>=X.Y), no upper bounds on core deps
