"""Data models for the pipeline."""

import json
from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class DataResult:
    """Standard result from any data source."""
    data: pd.Series | None           # Time series data (DatetimeIndex)
    source: str                         # "bcch" | "yahoo" | "fred" | "worldbank"
    series_id: str                      # Identifier of the series used
    country: str                        # Country code (ISO3 or "CHL")
    variable: str                       # "fx" | "ipc"
    coverage: tuple                     # (start_date_str, end_date_str)
    obs_count: int                      # Number of valid observations
    success: bool                       # Whether download succeeded
    error_message: str | None = None # Error detail if failed

    def to_dict(self):
        """Convert to dict for JSON serialization."""
        d = asdict(self)
        if self.data is not None:
            d['data'] = None  # Don't serialize the series itself
        return d


@dataclass
class CacheEntry:
    """Metadata for a cached data file."""
    key: str                            # Cache key: {country}_{variable}_{source}
    source: str                         # Data source name
    series_id: str                      # Series identifier
    download_timestamp: str             # ISO format timestamp
    data_range: tuple                   # (first_date, last_date)
    obs_count: int                      # Observations in the cached file

    def to_json(self):
        """Serialize to JSON."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize from JSON."""
        d = json.loads(json_str)
        return cls(**d)
