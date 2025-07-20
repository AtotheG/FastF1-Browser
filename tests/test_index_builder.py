import csv
from pathlib import Path
import tempfile
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.scripts.build_session_index import build_session_index


def create_cache(tmpdir: Path) -> Path:
    year = tmpdir / "2023"
    gp = year / "Test_GP"
    sess = gp / "2023-07-01_Practice_1"
    sess.mkdir(parents=True)
    (sess / "dummy.ff1pkl").touch()
    # create dummy db file as required by API but not used here
    (tmpdir / "fastf1.duckdb").touch()
    return tmpdir


def test_build_index_creates_and_updates():
    with tempfile.TemporaryDirectory() as d:
        cache = create_cache(Path(d))
        index_csv = cache / "session_index.csv"
        added = build_session_index(cache, index_csv)
        assert added == 1
        with index_csv.open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        # calling again should not add rows
        added = build_session_index(cache, index_csv)
        assert added == 0


def test_build_index_raises_for_missing_files():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)
        (path / "fastf1.duckdb").touch()
        index_csv = path / "session_index.csv"
        try:
            build_session_index(path, index_csv)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("expected FileNotFoundError")
