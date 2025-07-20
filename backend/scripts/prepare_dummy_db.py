"""Create a small dummy DuckDB database for local testing."""
import duckdb
from pathlib import Path


def create_dummy_db(
    db_path: Path = (
        Path(__file__).resolve().parent.parent / "data" / "dummy.duckdb"
    ),
):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute(
        "CREATE TABLE IF NOT EXISTS sessions("
        "id INTEGER PRIMARY KEY, name TEXT);"
    )
    con.execute(
        "INSERT INTO sessions(id, name) VALUES "
        "(1, 'Demo Session') ON CONFLICT DO NOTHING;"
    )
    con.close()


if __name__ == "__main__":
    db_path = create_dummy_db.__defaults__[0]
    create_dummy_db()
    print(f"Created dummy DB at {db_path}")
