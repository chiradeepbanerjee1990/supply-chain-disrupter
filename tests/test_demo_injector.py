import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.demo_injector import _pick_scenario_record, build_demo_payload

_STRICT_ROW = {"port": "Eastern Asia", "sku": "Canon Camera", "event_date": "2024-01-01", "history_points": 50}
_BROAD_ROW = {"port": "West Asia", "sku": "ASUS ROG Laptop", "event_date": "2024-02-01", "history_points": 40}
_ANY_ROW = {"port": "Western Europe", "sku": "LG OLED TV", "event_date": "2024-03-01", "history_points": 100}


def test_pick_scenario_record_uses_strict_pool_when_region_match_exists():
    with patch(
        "src.agents.demo_injector.fetch_scenario_options",
        return_value=[_STRICT_ROW, _ANY_ROW],
    ):
        with patch(
            "src.agents.demo_injector.fetch_scenario_options_for_regions"
        ) as mock_broad:
            record = _pick_scenario_record("taiwan_earthquake")

    assert record == _STRICT_ROW
    mock_broad.assert_not_called()  # tier 2 never needed, tier 1 already matched


def test_pick_scenario_record_falls_back_to_broad_regional_pool():
    # Regression test: Red Sea Crisis (region hint West Asia/North Africa)
    # has zero rows in the strict 4-category pool fetch_scenario_options()
    # returns, so it must NOT silently fall through to "any region" (tier
    # 3) — it should first retry with the region hint still applied, just
    # against the broader Electronics-inclusive pool.
    with patch(
        "src.agents.demo_injector.fetch_scenario_options",
        return_value=[_ANY_ROW],  # no West Asia/North Africa rows here
    ):
        with patch(
            "src.agents.demo_injector.fetch_scenario_options_for_regions",
            return_value=[_BROAD_ROW],
        ) as mock_broad:
            record = _pick_scenario_record("red_sea_crisis")

    assert record == _BROAD_ROW
    mock_broad.assert_called_once_with(["West Asia", "North Africa"])


def test_pick_scenario_record_falls_back_to_any_region_when_broad_pool_also_empty():
    with patch(
        "src.agents.demo_injector.fetch_scenario_options",
        return_value=[_ANY_ROW],
    ):
        with patch(
            "src.agents.demo_injector.fetch_scenario_options_for_regions",
            return_value=[],
        ):
            record = _pick_scenario_record("red_sea_crisis")

    assert record == _ANY_ROW  # tier 3: no region match anywhere, pick by history


def test_pick_scenario_record_clean_baseline_has_no_hint_skips_broad_tier():
    with patch(
        "src.agents.demo_injector.fetch_scenario_options",
        return_value=[_ANY_ROW],
    ):
        with patch(
            "src.agents.demo_injector.fetch_scenario_options_for_regions"
        ) as mock_broad:
            record = _pick_scenario_record("clean_baseline")

    assert record == _ANY_ROW
    mock_broad.assert_not_called()  # clean_baseline has no region hint at all


def test_build_demo_payload_red_sea_crisis_resolves_to_real_region_via_broad_pool():
    with patch(
        "src.agents.demo_injector.fetch_scenario_options",
        return_value=[_ANY_ROW],
    ):
        with patch(
            "src.agents.demo_injector.fetch_scenario_options_for_regions",
            return_value=[_BROAD_ROW],
        ):
            payload = build_demo_payload("red_sea_crisis", run_id="test-run")

    assert payload["affected_port"] == "West Asia"
    assert payload["sku"] == "ASUS ROG Laptop"
