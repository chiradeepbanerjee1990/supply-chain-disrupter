"""
conftest.py — Session-wide TruLens isolation.

OpenTelemetry's global TracerProvider binds exactly once per process and
cannot be overridden afterward (verified directly against the installed
SDK: calling trace.set_tracer_provider() after the first TruSession() call
in a process is a silent no-op — the original provider stays active).

This means whichever TruSession is created *first* anywhere in the whole
pytest run determines where every TruLens-instrumented test's spans get
exported for the rest of that run — clearing TruSession's own Pydantic
singleton per-test-file is NOT enough if some *other* test file runs first
and creates a session against the real database.

This fixture runs once, before any test in the session, and creates the
first-ever TruSession pointed at an isolated temp file — so
data/trulens/trulens.db (which the demo dashboard reads from) is protected
for the entire test run, regardless of test file order. Confirmed
necessary: 24 zero-cost junk records had accumulated in the real database
from exactly this gap across several prior test sessions.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session", autouse=True)
def _isolate_trulens_from_real_database(tmp_path_factory):
    import src.evaluation.trulens_integration.config as trulens_config

    isolated_db = tmp_path_factory.mktemp("trulens_session") / "trulens_test.db"
    trulens_config.DB_PATH = isolated_db
    # Deliberately NOT calling get_session() here — whichever test first
    # calls it (via run_with_trulens()/get_session() itself) still creates
    # the first-ever TruSession bound to the already-isolated DB_PATH set
    # above, achieving the same protection without eagerly forcing
    # TruLens's full import/init chain during session-fixture setup, which
    # was interfering with pytest's caplog capture in unrelated tests
    # (test_evaluate_ragas_integration.py) — root cause not fully pinned
    # down, but confirmed this ordering change resolves it without
    # reintroducing the real-database pollution it was added to prevent.
