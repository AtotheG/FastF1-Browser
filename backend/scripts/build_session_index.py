#!/usr/bin/env python
"""Create or update a session_index.csv for a FastF1 cache."""

import csv
import re
import sys
from pathlib import Path
from typing import Iterable, Dict, Set, Tuple, Optional

FIELDNAMES = ["session_id", "year", "event_name", "event_date", "session_type", "sid"]

SID2NAME = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Sprint Qualifying": "SQ",
    "Sprint Shootout": "SS",
    "Qualifying": "Q",
    "Sprint": "S",
    "Race": "R",
}

NAME2SID = {v: k for k, v in SID2NAME.items()}

FLAT_PATTERN = re.compile(
    r"(?P<year>\d{4})_(?P<event_date>\d{4}-\d{2}-\d{2})_(?P<event_name>.+)_(?P<sid>FP1|FP2|FP3|SQ|SS|Q|S|R)$"
)


def load_existing_keys(csv_path: Path) -> Set[str]:
    keys: Set[str] = set()
    if not csv_path.is_file():
        return keys
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        has_sid = "session_id" in reader.fieldnames
        for row in reader:
            if has_sid:
                keys.add(row["session_id"])
            else:
                keys.add(f'{row["year"]}_{row["event_name"].replace(" ", "_")}_{row["sid"]}')
    return keys


def cached_session_dirs(root: Path) -> Iterable[Tuple[Path, Path, Path]]:
    for ydir in root.glob("[12][09][0-9][0-9]"):
        if not ydir.is_dir():
            continue
        for gpdir in ydir.iterdir():
            for sdir in gpdir.iterdir():
                if sdir.is_dir() and any(sdir.glob("*.ff1pkl")):
                    yield ydir, gpdir, sdir


def build_row(year_dir: Path, gp_dir: Path, sess_dir: Path) -> Dict[str, str] | None:
    m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)", sess_dir.name)
    if not m:
        return None
    date_str, human = m.groups()
    human_std = human.replace("_", " ")
    sid = SID2NAME.get(human_std)
    if not sid:
        return None
    event_key = gp_dir.name
    session_id = f"{year_dir.name}_{event_key}_{sid}"
    return {
        "session_id": session_id,
        "year": int(year_dir.name),
        "event_name": gp_dir.name.replace("_", " "),
        "event_date": date_str,
        "session_type": human_std,
        "sid": sid,
    }


def build_row_from_file(pkl: Path) -> Optional[Dict[str, str]]:
    m = FLAT_PATTERN.match(pkl.stem)
    if not m:
        return None
    year = m.group("year")
    event_key = m.group("event_name")
    sid = m.group("sid")
    return {
        "session_id": pkl.stem,
        "year": int(year),
        "event_name": event_key.replace("_", " "),
        "event_date": m.group("event_date"),
        "session_type": NAME2SID.get(sid, sid),
        "sid": sid,
    }


def build_session_index(cache_dir: Path, index_csv: Path) -> int:
    """Create or update ``session_index.csv`` for ``cache_dir``.

    Returns the number of newly added rows.
    """

    known = load_existing_keys(index_csv)

    dirs = list(cached_session_dirs(cache_dir))
    flat_files = list(cache_dir.glob("*.ff1pkl"))
    if not dirs and not flat_files:
        raise FileNotFoundError("No ff1pkl files found in cache directory")

    new_rows = []
    for y, gp, sdir in dirs:
        row = build_row(y, gp, sdir)
        if row and row["session_id"] not in known:
            new_rows.append(row)
            known.add(row["session_id"])

    for pkl in flat_files:
        row = build_row_from_file(pkl)
        if row and row["session_id"] not in known:
            new_rows.append(row)
            known.add(row["session_id"])

    if new_rows:
        mode = "a" if index_csv.is_file() else "w"
        with index_csv.open(mode, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if mode == "w":
                writer.writeheader()
            writer.writerows(
                sorted(new_rows, key=lambda r: (r["year"], r["event_date"], r["sid"]))
            )

    return len(new_rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: build_session_index.py <cache_dir> <index_csv>")
        raise SystemExit(1)
    cache = Path(sys.argv[1])
    index = Path(sys.argv[2])
    try:
        added = build_session_index(cache, index)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
    print(f"Added {added} new rows to {index}")
