<<<<<<< HEAD
from typing import Any, Dict, List

=======
# from typing import Any, Dict, List

# from src.utils.rag_utils import build_rag_corpus_complete, query_chroma_rag
# from src.agents.state import NewsRiskSignal


# def query_news_signals(event_category: str) -> List[Dict[str, Any]]:
#     query_text = f"Supply chain disruption signals for {event_category} in electronics imports"
#     results = query_chroma_rag(query_text, n_results=8)
#     if not results:
#         try:
#             build_rag_corpus_complete(flush_existing=True)
#             results = query_chroma_rag(query_text, n_results=8)
#         except FileNotFoundError:
#             return []
        
#     parsed: List[Dict[str, Any]] = []
#     for idx, result in enumerate(results):
#         parsed.append(
#             {
#                 "source_id": f"rag-{idx}",
#                 "category": event_category,
#                 "severity": 0.5,    
#                 "summary": result["text"],
#                 "signal_tags": [event_category, "supply chain", "electronics"],
#             }
#         )
#     return parsed


# def build_news_signals(event_category: str) -> List[NewsRiskSignal]:
#     raw_signals = query_news_signals(event_category)
#     return [NewsRiskSignal(**signal) for signal in raw_signals]


from typing import Any, Dict, List, Optional
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
from src.utils.rag_utils import build_rag_corpus_complete, query_chroma_rag
from src.agents.state import NewsRiskSignal


<<<<<<< HEAD
def query_news_signals(event_category: str) -> List[Dict[str, Any]]:
    query_text = f"Supply chain disruption signals for {event_category} in electronics imports"
=======
# ─────────────────────────────────────────────────
# STEP 1: Build better RAG query
# ─────────────────────────────────────────────────

def build_rag_query(event_category: str) -> str:
    """
    Build a specific search query for ChromaDB
    based on disruption type.
    """
    category = event_category.lower().strip()

    if "chip" in category or "semiconductor" in category or "shortage" in category:
        return (
            "Electronics supply chain chip shortage risk, "
            "semiconductor shortage, wafer fabrication, "
            "foundry concentration, export controls, factory shutdown"
        )
    elif "port" in category or "closure" in category:
        return (
            "Port closure shipping delay rerouting, "
            "freight disruption inventory impact, "
            "port congestion vessel queue"
        )
    elif "weather" in category or "extreme" in category or "flood" in category:
        return (
            "Extreme weather port disruption flooding, "
            "storm delay logistics disruption, "
            "cyclone monsoon port closure"
        )
    elif "geo" in category or "political" in category or "sanction" in category:
        return (
            "Geopolitical risk supply chain disruption, "
            "sanctions export controls trade war, "
            "tariffs trade restrictions"
        )
    elif "supplier" in category or "lockdown" in category or "failure" in category:
        return (
            "Supplier failure lockdown factory shutdown, "
            "alternate supplier sourcing risk, "
            "procurement disruption"
        )
    elif "earthquake" in category or "disaster" in category:
        return (
            "Natural disaster earthquake supply chain, "
            "factory shutdown production halt, "
            "infrastructure damage logistics"
        )
    elif "freight" in category or "shipping" in category:
        return (
            "Freight rate spike shipping disruption, "
            "container capacity shortage logistics cost, "
            "Baltic index carrier delay"
        )
    else:
        return (
            f"Supply chain disruption risk {event_category}, "
            "electronics semiconductor logistics delay"
        )


# ─────────────────────────────────────────────────
# STEP 3: Helper functions for extraction
# ─────────────────────────────────────────────────

def detect_company(text: str) -> Optional[str]:
    """
    Detect company names mentioned in the text.
    Uses simple keyword matching.
    """
    companies = [
        "Foxconn", "TSMC", "ASML", "Samsung", "Intel",
        "NVIDIA", "Apple", "Toyota", "ON Semiconductor",
        "GlobalFoundries", "Microchip", "Analog Devices",
        "Cadence", "Realtek", "SMIC", "VisIC", "Qualcomm",
        "AMD", "Texas Instruments", "NXP", "Infineon"
    ]
    text_lower = text.lower()
    for company in companies:
        if company.lower() in text_lower:
            return company
    return None


def detect_location(text: str) -> Optional[str]:
    """
    Detect locations or routes mentioned in the text.
    Uses simple keyword matching.
    """
    locations = [
        "Taiwan", "China", "Japan", "Korea", "India",
        "USA", "US", "Europe", "Red Sea", "Suez Canal",
        "Singapore", "Vietnam", "Malaysia", "Caribbean",
        "Eastern Asia", "South Asia", "Israel", "Ukraine",
        "Russia", "Netherlands", "Germany"
    ]
    text_lower = text.lower()
    for location in locations:
        if location.lower() in text_lower:
            return location
    return None


def detect_event_category(text: str, fallback: str) -> str:
    """
    Detect event category from text content.
    Falls back to provided category if nothing detected.
    """
    categories = {
        "chip shortage": ["chip shortage", "semiconductor shortage", "chip supply"],
        "port closure": ["port closure", "port closed", "port congestion"],
        "supplier failure": ["supplier failure", "supplier shutdown", "supplier risk"],
        "factory shutdown": ["factory shutdown", "factory closure", "plant shutdown"],
        "export control": ["export control", "export ban", "trade restriction"],
        "geopolitical risk": ["geopolitical", "sanctions", "trade war", "tariff"],
        "freight disruption": ["freight", "shipping delay", "carrier", "container"],
        "weather disruption": ["weather", "cyclone", "flood", "storm", "monsoon"],
        "natural disaster": ["earthquake", "disaster", "tsunami", "hurricane"],
    }
    text_lower = text.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    return fallback


def detect_event_date(text: str) -> Optional[str]:
    """
    Detect year mentioned in the text.
    Simple year matching for 2020-2026.
    """
    years = ["2026", "2025", "2024", "2023", "2022", "2021", "2020"]
    for year in years:
        if year in text:
            return year
    return None


def summarize_text(text: str, max_chars: int = 400) -> str:
    """
    Shorten text to max_chars characters.
    Tries to cut at sentence boundary.
    """
    if len(text) <= max_chars:
        return text.strip()
    # Try to cut at last period before max_chars
    cut = text[:max_chars].rfind(".")
    if cut > max_chars // 2:
        return text[:cut + 1].strip()
    return text[:max_chars].strip() + "..."


# ─────────────────────────────────────────────────
# STEP 4: Calculate dynamic severity
# ─────────────────────────────────────────────────

def calculate_severity(
    text: str,
    selected_event_category: str,
    metadata: Dict[str, Any],
    company: Optional[str],
    location: Optional[str],
    multiple_sources_support: bool = False,
) -> float:
    """
    Calculate severity score dynamically based on
    text content, metadata and context.
    Instead of always returning 0.5!
    """
    # Start with base severity
    score = 0.3

    # +0.2 if text matches selected disruption type
    category_keywords = {
        "chip shortage": ["chip", "semiconductor", "shortage", "wafer", "foundry"],
        "port closure": ["port", "closure", "closed", "congestion", "vessel"],
        "extreme weather": ["weather", "cyclone", "flood", "storm", "monsoon"],
        "supplier lockdown": ["supplier", "lockdown", "shutdown", "failure"],
        "geopolitical": ["geopolitical", "sanctions", "war", "tariff", "trade"],
        "earthquake": ["earthquake", "disaster", "tsunami", "natural"],
        "freight disruption": ["freight", "shipping", "carrier", "container"],
    }
    text_lower = text.lower()
    category_lower = selected_event_category.lower()

    # Check if any keyword from selected category appears in text
    matched_keywords = category_keywords.get(category_lower, [])
    if any(kw in text_lower for kw in matched_keywords):
        score += 0.2

    # +0.2 if strong risk words found
    strong_risk_words = [
        "shutdown", "closure", "critical", "severe",
        "shortage", "sanctions", "export control",
        "war", "blockage", "earthquake", "flood",
        "strike", "disruption", "halt", "failure"
    ]
    if any(word in text_lower for word in strong_risk_words):
        score += 0.2

    # +0.1 if company detected
    if company:
        score += 0.1

    # +0.1 if location detected
    if location:
        score += 0.1

    # +0.1 if source is historical semiconductor event
    source_type = metadata.get("type", "")
    if source_type == "semiconductor_event":
        score += 0.1

    # +0.1 if multiple sources support same risk
    if multiple_sources_support:
        score += 0.1

    # Always cap between 0.0 and 1.0
    return round(min(score, 1.0), 3)


# ─────────────────────────────────────────────────
# STEP 2 + 5: Main query function with citations
# ─────────────────────────────────────────────────

def query_news_signals(event_category: str) -> List[Dict[str, Any]]:
    """
    Query ChromaDB with better query and return
    richer signals with dynamic severity.
    """
    # STEP 1: Use smart query
    query_text = build_rag_query(event_category)

>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
    results = query_chroma_rag(query_text, n_results=8)
    if not results:
        try:
            build_rag_corpus_complete(flush_existing=True)
            results = query_chroma_rag(query_text, n_results=8)
        except FileNotFoundError:
            return []
<<<<<<< HEAD
    parsed: List[Dict[str, Any]] = []
    for idx, result in enumerate(results):
        parsed.append(
            {
                "source_id": f"rag-{idx}",
                "category": event_category,
                "severity": 0.5,
                "summary": result["text"],
                "signal_tags": [event_category, "supply chain", "electronics"],
            }
        )
=======

    # Check if multiple results support same risk
    # (if 3+ results found, assume multiple sources)
    multiple_sources = len(results) >= 3

    parsed: List[Dict[str, Any]] = []
    for idx, result in enumerate(results):

        # STEP 2: Extract citation metadata
        text = result["text"]
        metadata = result.get("metadata", {})
        source_file = metadata.get("source", "Unknown Source")
        page_number = metadata.get("page", None)
        source_type = metadata.get("type", "unknown")
        distance = result.get("distance", 0.0)

        # Build citation string
        if page_number:
            citation = f"\n[Source: {source_file}, Page: {page_number}]"
        else:
            citation = f"\n[Source: {source_file}]"

        # STEP 3: Extract entities using helper functions
        company = detect_company(text)
        location = detect_location(text)
        detected_category = detect_event_category(text, event_category)
        event_date = detect_event_date(text)

        # Shorten summary
        summary = summarize_text(text, max_chars=400)
        summary_with_citation = summary + citation

        # STEP 4: Calculate dynamic severity
        severity = calculate_severity(
            text=text,
            selected_event_category=event_category,
            metadata=metadata,
            company=company,
            location=location,
            multiple_sources_support=multiple_sources,
        )

        # Build signal tags
        signal_tags = [event_category, "supply chain", "electronics"]
        if company:
            signal_tags.append(company)
        if location:
            signal_tags.append(location)
        if event_date:
            signal_tags.append(f"Date: {event_date}")

        # STEP 5: Return richer signal
        # Using Option A — adding citation inside summary
        # to keep NewsRiskSignal model unchanged
        parsed.append(
            {
                "source_id": f"rag-{idx}",
                "category": detected_category,
                "summary": summary_with_citation,
                "severity": severity,
                "signal_tags": signal_tags,

                # NEW separate fields (Milestone 3!)
                "source_file": source_file,
                "page_number": page_number if isinstance(page_number, int) else None,
                "source_type": source_type,
                "company": company,
                "location": location,
                "event_date": event_date,
                "signal_type": "static_context",
                "retrieval_distance": float(distance) if distance else None,
            }
        )

>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
    return parsed


def build_news_signals(event_category: str) -> List[NewsRiskSignal]:
    raw_signals = query_news_signals(event_category)
<<<<<<< HEAD
    return [NewsRiskSignal(**signal) for signal in raw_signals]
=======
    return [NewsRiskSignal(**signal) for signal in raw_signals]
>>>>>>> a0736fc (Milestone 1,2,3: Improved News Agent and Weather Agent)
