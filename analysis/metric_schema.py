"""Canonical metric and evidence schema used by every decision-facing module."""

from datetime import datetime
from typing import Any, Dict, Iterable, Optional


UNKNOWN = "UNKNOWN"
SECONDARY_SOURCE = "SECONDARY_MARKET_DATA"
SECONDARY_STATUS = "DERIVED_FROM_SECONDARY"
MISSING_TEXT = {"", "N/A", "NONE", "NULL", "UNAVAILABLE", "NOT VERIFIED", UNKNOWN}


def is_unknown(value: Any) -> bool:
    """Return true for an absent value without treating zero as absent."""
    return value is None or (isinstance(value, str) and value.strip().upper() in MISSING_TEXT)


def first_known(*values: Any) -> Any:
    """Return the first non-missing value while preserving valid zeros."""
    for value in values:
        if not is_unknown(value):
            return value
    return None


def _period_end(record: Dict[str, Any]) -> datetime:
    raw = record.get("period_end") or record.get("date") or ""
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min


def latest_statement(records: Any, preferred_scope: Optional[str] = None) -> Dict[str, Any]:
    """Pick the latest record within one explicit reporting scope.

    A requested standalone/consolidated scope is never mixed with another scope.
    Unknown scope is a valid isolated bucket, rather than an excuse to merge data.
    """
    candidates = [record for record in records if isinstance(record, dict)] if isinstance(records, list) else []
    if preferred_scope:
        candidates = [record for record in candidates if str(record.get("statement_scope") or UNKNOWN).upper() == preferred_scope.upper()]
    return max(candidates, key=_period_end, default={})


def metric(
    value: Any,
    formatted_string: Optional[str] = None,
    status: Optional[str] = None,
    explanation: str = "",
    reporting_period: str = UNKNOWN,
    statement_scope: str = UNKNOWN,
    period_end: Optional[str] = None,
    source_type: str = SECONDARY_SOURCE,
    verification_status: str = SECONDARY_STATUS,
) -> Dict[str, Any]:
    """Build the only metric shape consumed by decisions and renderers."""
    missing = is_unknown(value)
    return {
        "value": None if missing else value,
        "formatted_string": UNKNOWN if missing else (formatted_string or str(value)),
        "status": "unknown" if missing else (status or "neutral"),
        "explanation": explanation or "UNKNOWN",
        "evidence": {
            "source_type": source_type,
            "verification_status": verification_status,
            "reporting_period": reporting_period or UNKNOWN,
            "statement_scope": statement_scope or UNKNOWN,
            "period_end": period_end or UNKNOWN,
        },
    }


def apply_metric_schema(metrics: Dict[str, Any], period_record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Normalize every computed metric to the canonical metric/evidence shape."""
    record = period_record or {}
    evidence = {
        "reporting_period": record.get("reporting_period", UNKNOWN),
        "statement_scope": record.get("statement_scope", UNKNOWN),
        "period_end": record.get("period_end") or record.get("date") or UNKNOWN,
        "source_type": record.get("source_type", SECONDARY_SOURCE),
        "verification_status": SECONDARY_STATUS,
    }
    normalized: Dict[str, Any] = {}
    for group_name, group in metrics.items():
        if not isinstance(group, dict):
            normalized[group_name] = group
            continue
        normalized_group: Dict[str, Any] = {}
        for name, item in group.items():
            if item is None:
                normalized_group[name] = metric(None, **evidence)
            elif isinstance(item, dict) and "value" in item:
                existing_evidence = item.get("evidence", {}) if isinstance(item.get("evidence"), dict) else {}
                normalized_group[name] = metric(
                    item.get("value"),
                    item.get("formatted_string"),
                    item.get("status"),
                    item.get("explanation", ""),
                    existing_evidence.get("reporting_period", evidence["reporting_period"]),
                    existing_evidence.get("statement_scope", evidence["statement_scope"]),
                    existing_evidence.get("period_end", evidence["period_end"]),
                    existing_evidence.get("source_type", evidence["source_type"]),
                    existing_evidence.get("verification_status", evidence["verification_status"]),
                )
            else:
                normalized_group[name] = item
        normalized[group_name] = normalized_group
    return normalized
