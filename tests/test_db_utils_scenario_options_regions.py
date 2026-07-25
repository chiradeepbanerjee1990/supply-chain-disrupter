import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import src.utils.db_utils as db_utils
from src.utils.db_utils import fetch_scenario_options_for_regions


def _seed_daily_records(db_path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    """rows: (port, sku, event_date, category_name)"""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE daily_records (
            port TEXT, sku TEXT, event_date TEXT, category_name TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO daily_records (port, sku, event_date, category_name) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def test_fetch_scenario_options_for_regions_includes_electronics_category(tmp_path, monkeypatch):
    # West Asia/North Africa have zero rows in the strict 4-category pool
    # that fetch_scenario_options() uses, but real electronics history sits
    # under the broader 'Electronics' category — which that function
    # deliberately excludes (its docstring: sports/fashion items get
    # mislabeled 'Electronics' in the source dataset). This fallback
    # function scopes the broadened category set to specific regions only.
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_daily_records(
        db_path=tmp_path / "test.db",
        rows=[
            ("West Asia", "ASUS ROG Laptop", "2024-01-01", "Electronics"),
            ("West Asia", "ASUS ROG Laptop", "2024-01-02", "Electronics"),
            ("West Asia", "ASUS ROG Laptop", "2024-01-03", "Electronics"),
        ],
    )

    options = fetch_scenario_options_for_regions(["West Asia", "North Africa"])

    assert len(options) == 1
    assert options[0]["port"] == "West Asia"
    assert options[0]["sku"] == "ASUS ROG Laptop"
    assert options[0]["history_points"] == 3


def test_fetch_scenario_options_for_regions_still_requires_3_history_points(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_daily_records(
        db_path=tmp_path / "test.db",
        rows=[
            ("West Asia", "ASUS ROG Laptop", "2024-01-01", "Electronics"),
            ("West Asia", "ASUS ROG Laptop", "2024-01-02", "Electronics"),
        ],
    )

    options = fetch_scenario_options_for_regions(["West Asia"])

    assert options == []


def test_fetch_scenario_options_for_regions_only_returns_requested_regions(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_daily_records(
        db_path=tmp_path / "test.db",
        rows=[
            ("West Asia", "ASUS ROG Laptop", "2024-01-01", "Electronics"),
            ("West Asia", "ASUS ROG Laptop", "2024-01-02", "Electronics"),
            ("West Asia", "ASUS ROG Laptop", "2024-01-03", "Electronics"),
            ("Western Europe", "LG OLED TV", "2024-01-01", "Electronics"),
            ("Western Europe", "LG OLED TV", "2024-01-02", "Electronics"),
            ("Western Europe", "LG OLED TV", "2024-01-03", "Electronics"),
        ],
    )

    options = fetch_scenario_options_for_regions(["West Asia"])

    assert [o["port"] for o in options] == ["West Asia"]


def test_fetch_scenario_options_for_regions_empty_region_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_daily_records(db_path=tmp_path / "test.db", rows=[])

    assert fetch_scenario_options_for_regions([]) == []
