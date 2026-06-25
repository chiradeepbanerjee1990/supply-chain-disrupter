<<<<<<< HEAD
=======
# from pydantic import BaseModel, Field
# from typing import Any, Dict, List, Optional


# class EventMetadata(BaseModel):
#     disruption_type: str
#     affected_port: str
#     affected_route: str
#     severity: float
#     shock_duration_days: int
#     recovery_window_days: int
#     synthetic_ratio: float


# class NewsRiskSignal(BaseModel):
#     source_id: str
#     category: str
#     severity: float
#     summary: str
#     signal_tags: List[str]


# class ForecastResult(BaseModel):
#     prophet_forecast: List[Dict[str, Any]]
#     expected_drop_pct: float


# class SimulationResult(BaseModel):
#     stockout_probability_pct: float
#     expected_inventory_gap_pct: float
#     alternate_route: Optional[str]


# class MitigationAction(BaseModel):
#     summary: str
#     recommendations: List[str]
#     cost_delta: str


# class GlobalState(BaseModel):
#     event_metadata: Optional[EventMetadata] = None
#     config: Optional[Dict[str, Any]] = None
#     active_record: Optional[Dict[str, Any]] = None
#     news_signals: List[NewsRiskSignal] = Field(default_factory=list)
#     live_weather_severity: Optional[float] = None
#     risk_label: Optional[str] = None
#     risk_score_composite: Optional[float] = None
#     forecast_result: Optional[ForecastResult] = None
#     simulation_result: Optional[SimulationResult] = None
#     mitigation_action: Optional[MitigationAction] = None
#     agent_logs: List[str] = Field(default_factory=list)


>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class EventMetadata(BaseModel):
    disruption_type: str
    affected_port: str
    affected_route: str
    severity: float
    shock_duration_days: int
    recovery_window_days: int
    synthetic_ratio: float


<<<<<<< HEAD
class NewsRiskSignal(BaseModel):
=======
# ─────────────────────────────────────────────────
# MILESTONE 3: Updated NewsRiskSignal
# Added optional fields for richer signal data!
# ─────────────────────────────────────────────────

class NewsRiskSignal(BaseModel):
    # Original fields — unchanged
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
    source_id: str
    category: str
    severity: float
    summary: str
    signal_tags: List[str]

<<<<<<< HEAD
=======
    # NEW optional fields
    source_file: Optional[str] = None      # Which file chunk came from
    page_number: Optional[int] = None      # PDF page number
    source_type: Optional[str] = None      # semiconductor_event, playbook etc
    company: Optional[str] = None          # Detected company name
    location: Optional[str] = None         # Detected location/country
    event_date: Optional[str] = None       # Detected year/date
    signal_type: Optional[str] = None      # static_context or live_event
    retrieval_distance: Optional[float] = None  # ChromaDB similarity score

>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)

class ForecastResult(BaseModel):
    prophet_forecast: List[Dict[str, Any]]
    expected_drop_pct: float


class SimulationResult(BaseModel):
    stockout_probability_pct: float
    expected_inventory_gap_pct: float
    alternate_route: Optional[str]


class MitigationAction(BaseModel):
    summary: str
    recommendations: List[str]
    cost_delta: str


<<<<<<< HEAD
=======
# ─────────────────────────────────────────────────
# MILESTONE 3: Updated GlobalState
# Added weather explanation fields!
# ─────────────────────────────────────────────────

>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
class GlobalState(BaseModel):
    event_metadata: Optional[EventMetadata] = None
    config: Optional[Dict[str, Any]] = None
    active_record: Optional[Dict[str, Any]] = None
    news_signals: List[NewsRiskSignal] = Field(default_factory=list)
    live_weather_severity: Optional[float] = None
<<<<<<< HEAD
=======

    # NEW weather explanation fields
    weather_summary: Optional[str] = None          # Human readable summary
    weather_factors: Optional[Dict[str, Any]] = None  # Detailed factors

>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
    risk_label: Optional[str] = None
    risk_score_composite: Optional[float] = None
    forecast_result: Optional[ForecastResult] = None
    simulation_result: Optional[SimulationResult] = None
    mitigation_action: Optional[MitigationAction] = None
<<<<<<< HEAD
    agent_logs: List[str] = Field(default_factory=list)
=======
    agent_logs: List[str] = Field(default_factory=list)
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
