import csv
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.main import app


def test_cache_path_creates_index(tmp_path):
    # Prepare dummy cache directory with a duckdb file and a single ff1pkl file
    cache_dir = tmp_path
    (cache_dir / "fastf1.duckdb").write_text("")
    pkl_name = "2018_2018-03-25_Australian_Grand_Prix_FP1.ff1pkl"
    (cache_dir / pkl_name).write_text("")

    client = TestClient(app)
    response = client.post("/config/cache_path", params={"path": str(cache_dir)})
    assert response.status_code == 200

    index_file = cache_dir / "session_index.csv"
    assert index_file.is_file()

    with index_file.open() as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["session_id"] == pkl_name[:-7]
    assert rows[0]["sid"] == "FP1"


def test_cache_path_error_no_pickles(tmp_path):
    cache_dir = tmp_path
    (cache_dir / "fastf1.duckdb").write_text("")
    client = TestClient(app)
    response = client.post("/config/cache_path", params={"path": str(cache_dir)})
    assert response.status_code == 400
