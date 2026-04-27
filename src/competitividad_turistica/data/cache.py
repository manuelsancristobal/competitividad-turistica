"""CSV cache management for downloaded data."""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

from competitividad_turistica.config.settings import CACHE_DIR, CACHE_MAX_AGE_DAYS
from .models import CacheEntry

logger = logging.getLogger(__name__)


def cache_key(country: str, variable: str, source: str) -> str:
    """Generate cache key."""
    return f"{country.lower()}_{variable.lower()}_{source.lower()}"


def get_cache_path(key: str) -> tuple[Path, Path]:
    """Get CSV and metadata JSON paths for a cache key."""
    csv_path = CACHE_DIR / f"{key}.csv"
    meta_path = CACHE_DIR / f"{key}_meta.json"
    return csv_path, meta_path


def save_to_cache(key: str, series: pd.Series, metadata: dict) -> None:
    """Save series and metadata to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    csv_path, meta_path = get_cache_path(key)

    # Save CSV
    series.to_csv(csv_path, header=True)

    # Save metadata
    entry = CacheEntry(
        key=key,
        source=metadata.get("source", "unknown"),
        series_id=metadata.get("series_id", "unknown"),
        download_timestamp=datetime.now().isoformat(),
        data_range=(str(series.index[0])[:10], str(series.index[-1])[:10]) if len(series) > 0 else ("", ""),
        obs_count=len(series),
    )

    with open(meta_path, "w") as f:
        f.write(entry.to_json())

    logger.info(f"Cached {key}: {len(series)} observations")


def load_from_cache(key: str, max_age_days: int = CACHE_MAX_AGE_DAYS) -> tuple:
    """
    Load cached series and metadata if available and not expired.
    Returns (series, metadata) or (None, None) if not found or expired.
    """
    csv_path, meta_path = get_cache_path(key)

    if not csv_path.exists() or not meta_path.exists():
        return None, None

    try:
        # Check age
        with open(meta_path, "r") as f:
            entry = CacheEntry.from_json(f.read())

        download_time = datetime.fromisoformat(entry.download_timestamp)
        age = (datetime.now() - download_time).days

        if age > max_age_days:
            logger.debug(f"Cache {key} expired (age: {age} days)")
            return None, None

        # Load CSV
        series = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        series = series.squeeze()

        metadata = {
            "source": entry.source,
            "series_id": entry.series_id,
            "cache_age_days": age,
        }

        logger.info(f"Loaded from cache {key} (age: {age} days)")
        return series, metadata

    except Exception as e:
        logger.warning(f"Error loading cache {key}: {e}")
        return None, None


def clear_cache() -> None:
    """Clear all cache files."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.csv"):
            f.unlink()
        for f in CACHE_DIR.glob("*_meta.json"):
            f.unlink()
    logger.info("Cache cleared")


def cache_status() -> dict:
    """Get cache status."""
    if not CACHE_DIR.exists():
        return {"cached_files": 0, "cache_dir_size_mb": 0}

    files = list(CACHE_DIR.glob("*.csv"))
    size_bytes = sum(f.stat().st_size for f in files)

    return {
        "cached_files": len(files),
        "cache_dir_size_mb": round(size_bytes / (1024 * 1024), 2),
        "cache_dir": str(CACHE_DIR),
    }

