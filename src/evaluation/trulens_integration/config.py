"""
config.py — TruLens session + dashboard initialization.

Uses the current (2.8.x) TruSession API — NOT the deprecated Tru() class
from trulens-eval (removed from maintenance 2025-12-01).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from trulens.core import TruSession

DB_PATH = Path("data/trulens/trulens.db")


@lru_cache(maxsize=1)
def get_session() -> TruSession:
    """Process-lifetime TruSession backed by SQLite at data/trulens/trulens.db."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return TruSession(database_url=f"sqlite:///{DB_PATH}")


def launch_dashboard(port: int = 8502) -> None:
    """Launch the TruLens Streamlit dashboard as its own process on `port`.

    Imports trulens.dashboard lazily — it transitively pulls in Streamlit,
    matplotlib, and Jupyter, none of which the FastAPI service needs. Every
    other caller in this package only needs get_session(), so keeping this
    import inside the function body means importing this module (or the
    package's __init__.py, which imports launch_dashboard by name) never
    drags that weight into the API container.
    """
    from trulens.dashboard import run_dashboard

    run_dashboard(get_session(), port=port)
