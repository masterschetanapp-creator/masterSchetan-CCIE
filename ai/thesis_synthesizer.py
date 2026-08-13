"""Compatibility adapter for the retired independent thesis generator.

CCIE now produces its research conclusion through ``DecisionEngine``. Keeping a
second rule or LLM thesis engine would reintroduce a cross-view decision path,
so this module returns an explicitly limited placeholder for legacy callers.
"""

from typing import Any, Dict, List

from analysis.metric_schema import UNKNOWN, is_unknown


def get_metric_val(metrics: dict, group: str, key: str, fallback_label: str = UNKNOWN) -> str:
    item = metrics.get(group, {}).get(key) if isinstance(metrics.get(group), dict) else None
    if not isinstance(item, dict):
        return fallback_label
    value = item.get("formatted_string")
    return fallback_label if is_unknown(value) else str(value)


def get_metric_num(metrics: dict, group: str, key: str, default: Any = None) -> Any:
    item = metrics.get(group, {}).get(key) if isinstance(metrics.get(group), dict) else None
    value = item.get("value") if isinstance(item, dict) else None
    return default if is_unknown(value) else value


def generate_ctso(
    stock_data: dict,
    computed_metrics: dict,
    red_flags: List[Dict[str, Any]],
    sector_template: dict,
    news: list = None,
) -> Dict[str, Any]:
    """Return no independent thesis; use canonical decision support instead."""
    return {
        "archetype": "EVIDENCE_GATED",
        "golden_thread": "UNKNOWN - use the canonical Decision Support summary rather than a separate thesis engine.",
        "key_positive_drivers": [],
        "key_risk_factors": ["Independent thesis generation is disabled to prevent cross-view inconsistency."],
        "conviction_level": "UNKNOWN",
    }
