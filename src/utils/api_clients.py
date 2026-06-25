<<<<<<< HEAD
=======
# import requests
# from typing import Any, Dict

# OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


# def fetch_open_meteo(latitude: float, longitude: float, hourly: str = "windspeed_10m,precipitation,weathercode") -> Dict[str, Any]:
#     try:
#         response = requests.get(
#             OPEN_METEO_URL,
#             params={
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "hourly": hourly,
#                 "timezone": "UTC",
#             },
#             timeout=10,
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as exc:
#         raise RuntimeError(f"Open-Meteo API request failed: {exc}") from exc


# def compute_weather_severity(weather_payload: Dict[str, Any]) -> float:
#     try:
#         hourly = weather_payload.get("hourly", {})
#         wind = hourly.get("windspeed_10m", [])
#         precip = hourly.get("precipitation", [])
#         if not wind or not precip:
#             return 0.0
#         avg_wind = sum(wind) / len(wind)
#         avg_precip = sum(precip) / len(precip)
#         severity = min(1.0, (avg_wind / 30.0) + (avg_precip / 50.0))
#         return round(severity, 3)
#     except Exception as exc:
#         raise RuntimeError(f"Failed to compute weather severity: {exc}") from exc

>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
import requests
from typing import Any, Dict

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


<<<<<<< HEAD
def fetch_open_meteo(latitude: float, longitude: float, hourly: str = "windspeed_10m,precipitation,weathercode") -> Dict[str, Any]:
=======
# ─────────────────────────────────────────────────
# STEP 1: Fetch weather data from Open-Meteo API
# Same as before — no changes needed here
# ─────────────────────────────────────────────────

def fetch_open_meteo(
    latitude: float,
    longitude: float,
    hourly: str = "windspeed_10m,precipitation,weathercode"
) -> Dict[str, Any]:
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": hourly,
                "timezone": "UTC",
            },
            timeout=10,
<<<<<<< HEAD
=======
            verify=False,
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
<<<<<<< HEAD
        raise RuntimeError(f"Open-Meteo API request failed: {exc}") from exc


def compute_weather_severity(weather_payload: Dict[str, Any]) -> float:
    try:
        hourly = weather_payload.get("hourly", {})
        wind = hourly.get("windspeed_10m", [])
        precip = hourly.get("precipitation", [])
        if not wind or not precip:
            return 0.0
        avg_wind = sum(wind) / len(wind)
        avg_precip = sum(precip) / len(precip)
        severity = min(1.0, (avg_wind / 30.0) + (avg_precip / 50.0))
        return round(severity, 3)
    except Exception as exc:
        raise RuntimeError(f"Failed to compute weather severity: {exc}") from exc
=======
        raise RuntimeError(
            f"Open-Meteo API request failed: {exc}"
        ) from exc


# ─────────────────────────────────────────────────
# STEP 2: Improved severity calculation
# Now calculates separate factor scores!
# ─────────────────────────────────────────────────

def compute_weather_severity(
    weather_payload: Dict[str, Any]
) -> float:
    """
    Calculate overall weather severity score.
    Returns a single float between 0.0 and 1.0.
    Now uses wind + precipitation + weather codes!
    """
    try:
        factors = compute_weather_factors(weather_payload)
        return factors["severity"]
    except Exception as exc:
        raise RuntimeError(
            f"Failed to compute weather severity: {exc}"
        ) from exc


# ─────────────────────────────────────────────────
# STEP 2: Compute separate weather factor scores
# ─────────────────────────────────────────────────

# Bad weather codes from Open-Meteo:
# 51-67: Drizzle and Rain
# 71-77: Snow
# 80-82: Rain showers
# 85-86: Snow showers
# 95:    Thunderstorm
# 96-99: Thunderstorm with hail
BAD_WEATHER_CODES = {
    51, 53, 55,           # Drizzle
    61, 63, 65,           # Rain
    66, 67,               # Freezing rain
    71, 73, 75, 77,       # Snow
    80, 81, 82,           # Rain showers
    85, 86,               # Snow showers
    95, 96, 99            # Thunderstorm
}


def compute_weather_factors(
    weather_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute separate weather factor scores and
    return detailed explanation.

    Returns:
        severity         : overall score 0.0-1.0
        wind_score       : wind contribution
        precipitation_score : rain contribution
        weather_code_score  : bad weather code contribution
        max_wind_speed   : highest wind speed recorded
        max_precipitation: highest rainfall recorded
        weather_summary  : human readable explanation
    """
    try:
        hourly = weather_payload.get("hourly", {})

        # ── Wind Score ──────────────────────────────
        wind = hourly.get("windspeed_10m", [])
        if wind:
            avg_wind = sum(wind) / len(wind)
            max_wind = max(wind)
            # Normalize: 40 km/h = score of 1.0
            wind_score = min(1.0, avg_wind / 40.0)
        else:
            avg_wind = 0.0
            max_wind = 0.0
            wind_score = 0.0

        # ── Precipitation Score ──────────────────────
        precip = hourly.get("precipitation", [])
        if precip:
            avg_precip = sum(precip) / len(precip)
            max_precip = max(precip)
            # Normalize: 25mm = score of 1.0
            precipitation_score = min(1.0, avg_precip / 25.0)
        else:
            avg_precip = 0.0
            max_precip = 0.0
            precipitation_score = 0.0

        # ── Weather Code Score ───────────────────────
        codes = hourly.get("weathercode", [])
        if codes:
            # Check if any bad weather codes exist
            bad_codes_found = [
                c for c in codes
                if int(c) in BAD_WEATHER_CODES
            ]
            if bad_codes_found:
                # More bad codes = higher score
                bad_ratio = len(bad_codes_found) / len(codes)
                weather_code_score = min(0.3, bad_ratio * 0.3)
            else:
                weather_code_score = 0.0
        else:
            weather_code_score = 0.0

        # ── Overall Severity ─────────────────────────
        severity = min(1.0,
            wind_score +
            precipitation_score +
            weather_code_score
        )
        severity = round(severity, 3)

        # ── Weather Summary Text ─────────────────────
        weather_summary = build_weather_summary(
            wind_score,
            precipitation_score,
            weather_code_score,
            max_wind,
            max_precip,
            severity
        )

        return {
            "severity": severity,
            "wind_score": round(wind_score, 3),
            "precipitation_score": round(precipitation_score, 3),
            "weather_code_score": round(weather_code_score, 3),
            "max_wind_speed": round(max_wind, 1),
            "max_precipitation": round(max_precip, 1),
            "weather_summary": weather_summary,
            "signal_type": "live_event",
        }

    except Exception as exc:
        # Safe fallback — never crash the workflow!
        return {
            "severity": 0.0,
            "wind_score": 0.0,
            "precipitation_score": 0.0,
            "weather_code_score": 0.0,
            "max_wind_speed": 0.0,
            "max_precipitation": 0.0,
            "weather_summary": "Weather data unavailable.",
            "signal_type": "live_event",
        }


# ─────────────────────────────────────────────────
# STEP 3: Build human readable weather summary
# ─────────────────────────────────────────────────

def build_weather_summary(
    wind_score: float,
    precipitation_score: float,
    weather_code_score: float,
    max_wind: float,
    max_precip: float,
    severity: float,
) -> str:
    """
    Build a human readable weather risk summary.
    Example:
    "High wind (45 km/h) and heavy rainfall (12mm)
     may increase port delay risk."
    """
    parts = []

    # Wind description
    if wind_score >= 0.7:
        parts.append(f"Very high wind ({max_wind:.1f} km/h)")
    elif wind_score >= 0.4:
        parts.append(f"High wind ({max_wind:.1f} km/h)")
    elif wind_score >= 0.2:
        parts.append(f"Moderate wind ({max_wind:.1f} km/h)")

    # Precipitation description
    if precipitation_score >= 0.7:
        parts.append(f"very heavy rainfall ({max_precip:.1f} mm)")
    elif precipitation_score >= 0.4:
        parts.append(f"heavy rainfall ({max_precip:.1f} mm)")
    elif precipitation_score >= 0.2:
        parts.append(f"moderate rainfall ({max_precip:.1f} mm)")

    # Weather code description
    if weather_code_score >= 0.2:
        parts.append("severe weather conditions detected")
    elif weather_code_score >= 0.1:
        parts.append("adverse weather conditions detected")

    # Build final summary
    if not parts:
        if severity < 0.2:
            return "Weather conditions are normal. Low disruption risk."
        else:
            return "Mild weather conditions. Minimal disruption risk."

    summary = " and ".join(parts)

    # Add impact statement based on severity
    if severity >= 0.7:
        impact = "High risk of port closure and logistics disruption."
    elif severity >= 0.4:
        impact = "May increase port delay and logistics risk."
    else:
        impact = "Minor impact on logistics expected."

    return f"{summary} — {impact}"


# ─────────────────────────────────────────────────
# STEP 4: Adjust severity by disruption type
# Weather matters more for some disruptions!
# ─────────────────────────────────────────────────

def adjust_weather_for_disruption(
    severity: float,
    disruption_type: str,
) -> float:
    """
    Adjust weather severity based on disruption type.
    Weather matters MORE for port/weather disruptions.
    Weather matters LESS for chip/geopolitical disruptions.
    """
    disruption = disruption_type.lower()

    # Weather is VERY relevant for these:
    if any(word in disruption for word in [
        "extreme weather", "port closure",
        "flood", "storm", "earthquake"
    ]):
        # Keep full severity
        adjusted = severity * 1.0

    # Weather is SOMEWHAT relevant for these:
    elif any(word in disruption for word in [
        "supplier lockdown", "freight", "shipping"
    ]):
        # Reduce slightly
        adjusted = severity * 0.8

    # Weather is LESS relevant for these:
    elif any(word in disruption for word in [
        "chip shortage", "semiconductor",
        "export control", "geopolitical", "sanction"
    ]):
        # Reduce significantly
        adjusted = severity * 0.5

    else:
        # Default — keep as is
        adjusted = severity * 0.7

    return round(min(1.0, adjusted), 3)
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
