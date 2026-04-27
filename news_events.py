from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


EventType = str


@dataclass(frozen=True)
class NewsEvent:
    event_type: EventType
    polarity: int  # -1 negative, 0 neutral, +1 positive
    confidence: float  # 0..1 (pattern confidence)


DEFAULT_EVENT_TAXONOMY: Dict[EventType, Dict] = {
    "ManagementChange": {"keywords": ["ceo", "cfo", "chairman", "resigns", "steps down", "appointed", "names"], "polarity": 0, "severity": "medium"},
    "EarningsGuidance": {"keywords": ["guidance", "outlook", "raises", "cuts", "beats", "misses", "earnings"], "polarity": 0, "severity": "high"},
    "M&A": {"keywords": ["acquire", "acquisition", "merger", "takeover", "deal"], "polarity": 0, "severity": "high"},
    "Regulatory": {"keywords": ["sec", "ftc", "doj", "regulator", "antitrust", "probe", "investigation"], "polarity": -1, "severity": "high"},
    "Litigation": {"keywords": ["lawsuit", "sued", "settlement", "court", "trial"], "polarity": -1, "severity": "medium"},
    "ProductLaunch": {"keywords": ["launch", "unveils", "introduces", "releases", "product"], "polarity": +1, "severity": "low"},
    "R&D": {"keywords": ["r&d", "research", "breakthrough", "patent", "innovation"], "polarity": +1, "severity": "low"},
    "Funding/Investors": {"keywords": ["investment", "investor", "stake", "funding", "raises", "round"], "polarity": +1, "severity": "medium"},
    "GeopoliticalExposure": {"keywords": ["sanction", "tariff", "war", "conflict", "export controls", "geopolitical"], "polarity": -1, "severity": "high"},
    "SupplyChain": {"keywords": ["supply chain", "shortage", "disruption", "logistics", "inventory"], "polarity": -1, "severity": "medium"},
    "MarketReaction": {"keywords": ["surge", "plunge", "rally", "sell-off", "volatility", "crash"], "polarity": 0, "severity": "high"},
    "DividendChange": {"keywords": ["dividend", "payout", "yield", "suspends", "increases", "cuts"], "polarity": 0, "severity": "medium"},
    "CreditRating": {"keywords": ["rating", "upgrade", "downgrade", "junk", "investment grade", "moody's", "s&p"], "polarity": 0, "severity": "high"},
    "LaborIssues": {"keywords": ["strike", "union", "layoff", "furlough", "job cuts", "workforce"], "polarity": -1, "severity": "medium"},
    "CommodityImpact": {"keywords": ["oil", "gas", "commodity", "energy", "price", "inflation"], "polarity": 0, "severity": "medium"},
}


TRUSTED_SOURCES = ("reuters", "bloomberg", "wall street journal", "wsj", "financial times", "ft", "cnbc", "associated press", "ap")
QUESTIONABLE_SOURCES = ("blog", "substack", "twitter", "x.com", "reddit", "tiktok", "telegram", "youtube")
MODERATE_SOURCES = ("yahoo finance", "marketwatch", "seeking alpha", "benzinga", "motley fool")


def source_credibility_weight(source: str) -> float:
    s = (source or "").lower()
    if any(t in s for t in TRUSTED_SOURCES):
        return 1.0
    if any(t in s for t in MODERATE_SOURCES):
        return 0.8
    if any(t in s for t in QUESTIONABLE_SOURCES):
        return 0.5
    return 0.7  # Default for unknown sources


def recency_weight(published_unix: Optional[int], half_life_days: float = 3.0) -> float:
    """
    Exponential decay: weight = 0.5^(age/half_life).
    """
    if not published_unix:
        return 0.7
    # Support ISO timestamps as well as unix seconds
    if isinstance(published_unix, str):
        try:
            dt = datetime.fromisoformat(published_unix.replace("Z", "+00:00"))
            published_unix = int(dt.replace(tzinfo=timezone.utc).timestamp())
        except Exception:
            return 0.7
    now = datetime.now(tz=timezone.utc).timestamp()
    age_days = max(0.0, (now - float(published_unix)) / 86400.0)
    return float(0.5 ** (age_days / max(0.5, half_life_days)))


def detect_events(title: str) -> List[NewsEvent]:
    t = (title or "").lower()
    events: List[NewsEvent] = []
    for event_type, spec in DEFAULT_EVENT_TAXONOMY.items():
        kws = spec.get("keywords", [])
        if any(kw in t for kw in kws):
            base_pol = int(spec.get("polarity", 0))
            severity = spec.get("severity", "medium")
            
            # Add directional hints
            pol = base_pol
            if event_type == "EarningsGuidance":
                if any(w in t for w in ["raises", "beats", "surge", "record"]):
                    pol = +1
                elif any(w in t for w in ["cuts", "misses", "warns", "slumps"]):
                    pol = -1
            if event_type == "ManagementChange":
                if any(w in t for w in ["resigns", "steps down", "fired"]):
                    pol = -1
                elif any(w in t for w in ["appointed", "names", "promotes"]):
                    pol = 0
            if event_type == "DividendChange":
                if any(w in t for w in ["increases", "raises", "hikes"]):
                    pol = +1
                elif any(w in t for w in ["cuts", "suspends", "eliminates"]):
                    pol = -1
            if event_type == "CreditRating":
                if any(w in t for w in ["upgrade", "positive", "affirmed"]):
                    pol = +1
                elif any(w in t for w in ["downgrade", "negative", "cut"]):
                    pol = -1
            
            # Confidence based on severity and keyword strength
            base_conf = 0.65
            if severity == "high":
                base_conf = 0.75
            elif severity == "low":
                base_conf = 0.55
            
            # Boost confidence if multiple keywords match
            keyword_matches = sum(1 for kw in kws if kw in t)
            if keyword_matches >= 2:
                base_conf = min(0.85, base_conf + 0.1)
            
            events.append(NewsEvent(event_type=event_type, polarity=pol, confidence=base_conf))
    return events


def headline_sentiment_score(title: str) -> float:
    """
    Lightweight sentiment for headlines.
    If TextBlob is installed, use it; otherwise fallback to keyword polarity.
    """
    text = (title or "").strip()
    if not text:
        return 0.0

    try:
        from textblob import TextBlob

        return float(TextBlob(text).sentiment.polarity)
    except Exception:
        t = text.lower()
        pos = sum(w in t for w in ["beat", "beats", "surge", "record", "growth", "profit", "upgrade", "wins"])
        neg = sum(w in t for w in ["miss", "misses", "warn", "slump", "lawsuit", "downgrade", "fraud", "probe"])
        if pos == neg:
            return 0.0
        return float((pos - neg) / max(3, pos + neg))


def enrich_news_items(items: List[Dict]) -> List[Dict]:
    enriched: List[Dict] = []
    for it in items or []:
        title = it.get("title", "")
        published = it.get("published")
        source = it.get("source", "")

        cred = float(source_credibility_weight(source))
        rec = float(recency_weight(published))
        sent = float(headline_sentiment_score(title))
        events = detect_events(title)

        # Event contribution (bounded, weighted by severity)
        event_score = 0.0
        severity_boost = 1.0
        if events:
            # Calculate average event score
            event_score = float(sum(e.polarity * e.confidence for e in events) / max(1, len(events)))
            # Boost weight if high-severity events are present
            high_severity_count = sum(1 for e in events if DEFAULT_EVENT_TAXONOMY.get(e.event_type, {}).get("severity") == "high")
            if high_severity_count > 0:
                severity_boost = 1.15
        effective = float((0.7 * sent + 0.3 * event_score) * cred * rec * severity_boost)

        # Include severity in event output
        events_with_severity = []
        for e in events:
            event_dict = e.__dict__.copy()
            event_dict["severity"] = DEFAULT_EVENT_TAXONOMY.get(e.event_type, {}).get("severity", "medium")
            events_with_severity.append(event_dict)

        enriched.append(
            {
                **it,
                "credibility_weight": round(cred, 3),
                "recency_weight": round(rec, 3),
                "headline_sentiment": round(sent, 3),
                "events": events_with_severity,
                "effective_sentiment": round(float(max(-1.0, min(1.0, effective))), 3),
                "severity_boost": round(severity_boost, 3),
            }
        )
    return enriched


def aggregate_effective_sentiment(enriched_items: List[Dict]) -> Tuple[float, int]:
    vals = [float(it.get("effective_sentiment") or 0.0) for it in enriched_items or []]
    if not vals:
        return 0.0, 0
    return float(sum(vals) / len(vals)), len(vals)

