import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import src.utils.db_utils as db_utils
from src.utils.db_utils import fetch_recent_ensemble_signals


def _seed_risk_classifications(db_path: Path, rows: list[tuple[str, dict | None]]) -> None:
    """rows: (run_ts, full_result_json_dict_or_None)"""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE risk_classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_ts TEXT,
            full_result_json TEXT
        )
        """
    )
    for run_ts, payload in rows:
        conn.execute(
            "INSERT INTO risk_classifications (run_ts, full_result_json) VALUES (?, ?)",
            (run_ts, json.dumps(payload) if payload is not None else None),
        )
    conn.commit()
    conn.close()


def _full_result(rule_label, distilbert_label, llm_label):
    return {
        "rule_signal": {"escalated_label": rule_label},
        "distilbert_signal": {"predicted_label": distilbert_label} if distilbert_label else None,
        "llm_signal": {"predicted_label": llm_label} if llm_label else None,
        "judge_verdict": None,
    }


def test_fetch_recent_ensemble_signals_extracts_all_three_labels(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_risk_classifications(
        tmp_path / "test.db",
        rows=[("2026-07-18 12:00:00", _full_result("HIGH", "HIGH", "CRITICAL"))],
    )

    triples = fetch_recent_ensemble_signals(30)

    assert triples == [("HIGH", "HIGH", "CRITICAL")]


def test_fetch_recent_ensemble_signals_skips_rows_missing_distilbert(tmp_path, monkeypatch):
    # DistilBERT is frequently absent in practice (no fine-tuned model
    # configured is the default local setup) — a row missing any of the
    # three signals isn't usable for a 3-signal agreement comparison.
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_risk_classifications(
        tmp_path / "test.db",
        rows=[
            ("2026-07-18 12:00:00", _full_result("HIGH", None, "CRITICAL")),
            ("2026-07-18 12:01:00", _full_result("HIGH", "HIGH", "HIGH")),
        ],
    )

    triples = fetch_recent_ensemble_signals(30)

    assert triples == [("HIGH", "HIGH", "HIGH")]


def test_fetch_recent_ensemble_signals_skips_null_full_result_json(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_risk_classifications(
        tmp_path / "test.db",
        rows=[("2026-07-18 12:00:00", None)],
    )

    assert fetch_recent_ensemble_signals(30) == []


def test_fetch_recent_ensemble_signals_skips_malformed_json(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    conn = sqlite3.connect(tmp_path / "test.db")
    conn.execute(
        "CREATE TABLE risk_classifications (id INTEGER PRIMARY KEY AUTOINCREMENT, run_ts TEXT, full_result_json TEXT)"
    )
    conn.execute(
        "INSERT INTO risk_classifications (run_ts, full_result_json) VALUES (?, ?)",
        ("2026-07-18 12:00:00", "{not valid json"),
    )
    conn.commit()
    conn.close()

    assert fetch_recent_ensemble_signals(30) == []


def test_fetch_recent_ensemble_signals_respects_days_window(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    _seed_risk_classifications(
        tmp_path / "test.db",
        rows=[
            ("2020-01-01 00:00:00", _full_result("LOW", "LOW", "LOW")),  # far outside window
        ],
    )

    assert fetch_recent_ensemble_signals(30) == []
