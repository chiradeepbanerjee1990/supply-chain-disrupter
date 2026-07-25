import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import src.evaluation.trulens_integration.config as trulens_config
from src.evaluation.trulens_integration.config import get_session, launch_dashboard


def test_get_session_returns_same_instance_on_repeated_calls():
    s1 = get_session()
    s2 = get_session()
    assert s1 is s2


def test_get_session_uses_configured_db_path():
    # Checks against the *current* config.DB_PATH rather than the literal
    # "data/trulens/trulens.db" production default: under pytest,
    # tests/conftest.py's session-scoped isolation fixture always points
    # DB_PATH at an isolated temp file before any test runs (OpenTelemetry's
    # global TracerProvider binds once per process, so the real path can
    # never safely be used here) — this test is about get_session()
    # correctly using whatever config.DB_PATH is set to, not about the
    # production default specifically, which is exercised for real by
    # Task 13-style manual verification instead.
    session = get_session()
    assert str(trulens_config.DB_PATH) in str(session.connector.db.engine.url)


def test_launch_dashboard_calls_run_dashboard_with_port_8502():
    with patch("src.evaluation.trulens_integration.config.run_dashboard") as mock_run:
        launch_dashboard()
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs.get("port") == 8502
