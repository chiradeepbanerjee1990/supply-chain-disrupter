import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    pipeline, live_feed, risk, forecast, simulation, mitigation, observability, guardrails, rag, admin,
    trulens,
)
from src.utils.db_utils import ensure_schema, ensure_sku_id_columns


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Without this, agent_execution_log/etc. only exist once some pipeline
    # run has called ensure_schema() (langgraph_engine.py) — fine locally
    # where outputs/supply_chain.db persists across restarts, but a fresh
    # container (e.g. Railway) 500s on the very first GET /api/pipeline/status
    # poll, before any run has ever happened.
    ensure_schema()
    ensure_sku_id_columns()
    yield


app = FastAPI(
    title="Supply Chain Command Center API",
    version="0.1.0",
    description="Backend for the L1-L7 LangGraph pipeline dashboard. "
                 "Day 1: every endpoint below returns fixture JSON matching the final schema. "
                 "Day 8 replaces fixtures.py reads with real SQLite/ChromaDB reads — "
                 "no route signatures change.",
    lifespan=lifespan,
)

_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(live_feed.router, prefix="/api/live-feed", tags=["live-feed"])
app.include_router(risk.router, prefix="/api/risk-classification", tags=["risk"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["forecast"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(mitigation.router, prefix="/api/mitigation", tags=["mitigation"])
app.include_router(observability.router, prefix="/api/observability", tags=["observability"])
app.include_router(guardrails.router, prefix="/api/guardrails", tags=["guardrails"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(trulens.router, prefix="/api/trulens", tags=["trulens"])


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "real-data"}
