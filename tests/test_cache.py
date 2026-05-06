"""Tests for data/cache.py."""

import json

import pandas as pd


class TestCacheKey:
    def test_lowercase(self):
        from competitividad_turistica.data.cache import cache_key

        assert cache_key("USA", "FX", "BCCH") == "usa_fx_bcch"

    def test_format(self):
        from competitividad_turistica.data.cache import cache_key

        result = cache_key("bra", "ipc", "fred")
        assert result == "bra_ipc_fred"


class TestSaveAndLoad:
    def test_round_trip(self, tmp_path, monkeypatch):
        monkeypatch.setattr("competitividad_turistica.data.cache.CACHE_DIR", tmp_path)
        from competitividad_turistica.data.cache import load_from_cache, save_to_cache

        dates = pd.date_range("2020-01-01", periods=12, freq="MS")
        series = pd.Series(range(12), index=dates, name="value", dtype=float)
        metadata = {"source": "test", "series_id": "test_001"}

        save_to_cache("test_key", series, metadata)
        loaded, meta = load_from_cache("test_key", max_age_days=1)

        assert loaded is not None
        assert len(loaded) == 12
        assert meta["source"] == "test"

    def test_expired_cache(self, tmp_path, monkeypatch):
        monkeypatch.setattr("competitividad_turistica.data.cache.CACHE_DIR", tmp_path)
        from competitividad_turistica.data.cache import load_from_cache, save_to_cache

        dates = pd.date_range("2020-01-01", periods=5, freq="MS")
        series = pd.Series(range(5), index=dates, name="value", dtype=float)

        save_to_cache("old_key", series, {"source": "x", "series_id": "x"})

        # Manually backdate the metadata
        meta_path = tmp_path / "old_key_meta.json"
        meta = json.loads(meta_path.read_text())
        meta["download_timestamp"] = "2020-01-01T00:00:00"
        meta_path.write_text(json.dumps(meta))

        loaded, _ = load_from_cache("old_key", max_age_days=7)
        assert loaded is None

    def test_missing_cache(self, tmp_path, monkeypatch):
        monkeypatch.setattr("competitividad_turistica.data.cache.CACHE_DIR", tmp_path)
        from competitividad_turistica.data.cache import load_from_cache

        loaded, meta = load_from_cache("nonexistent_key")
        assert loaded is None
        assert meta is None


class TestCacheStatus:
    def test_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr("competitividad_turistica.data.cache.CACHE_DIR", tmp_path)
        from competitividad_turistica.data.cache import cache_status

        status = cache_status()
        assert status["cached_files"] == 0

    def test_with_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr("competitividad_turistica.data.cache.CACHE_DIR", tmp_path)
        (tmp_path / "a.csv").write_text("x")
        (tmp_path / "b.csv").write_text("y")

        from competitividad_turistica.data.cache import cache_status

        status = cache_status()
        assert status["cached_files"] == 2
