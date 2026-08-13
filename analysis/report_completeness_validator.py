"""Evidence-based report completeness accounting."""

from typing import Any, Callable, Dict, List, Tuple

from analysis.metric_schema import UNKNOWN, is_unknown


EXPECTED_26_SECTIONS = [
    "1. Understand in 30 Seconds", "2. Primary Strengths & Risk Factors", "3. Valuation & Price Assessment",
    "4. Business Segmental Breakdown", "5. Shareholding Pattern & Ownership", "6. Profitability Trajectory",
    "7. Revenue Growth & Topline Momentum", "8. Balance Sheet & Solvency Structure", "9. Cash Flow & Profit Quality",
    "10. Capital Allocation & Capex", "11. Working Capital & Cash Conversion", "12. Forensic Red Flags",
    "13. Peer Valuation Comparison", "14. 7-Point Tip Check Result", "15. What to Monitor Next",
    "16. Distribution Reach & Operational Scale", "17. Management & Governance Structure", "18. Central Investment Thesis (CTSO)",
    "19. Company History & Milestones", "20. Dividends & Capital Return History", "21. Sector-Specific Operating Drivers",
    "22. Group & Subsidiary Structure", "23. Macro & Regulatory Realization Drivers", "24. Source Evidence & Fact Tracking",
    "25. Report Consistency & Quality Check", "26. Research Status & Verdict Summary",
]


def _has_metric(metrics: dict, group: str, name: str) -> bool:
    item = metrics.get(group, {}).get(name) if isinstance(metrics.get(group), dict) else None
    return isinstance(item, dict) and not is_unknown(item.get("value"))


class ReportCompletenessValidator:
    """Count only sections backed by an actual module or canonical metric."""

    def validate_completeness(self, dossier: Dict[str, Any]) -> Dict[str, Any]:
        modules = dossier.get("modules", {}) if isinstance(dossier, dict) else {}
        metrics = modules.get("computed_metrics", {}) if isinstance(modules.get("computed_metrics"), dict) else {}
        decision = dossier.get("decision_support") or modules.get("decision_support", {})
        raw = modules.get("raw_data", {}) if isinstance(modules.get("raw_data"), dict) else {}
        consistency = dossier.get("consistency_check", {})

        checks: List[Tuple[str, bool]] = [
            (EXPECTED_26_SECTIONS[0], bool(decision.get("tip_check"))),
            (EXPECTED_26_SECTIONS[1], bool(decision.get("positives")) and bool(decision.get("risks"))),
            (EXPECTED_26_SECTIONS[2], _has_metric(metrics, "valuation", "pe_ratio") or _has_metric(metrics, "valuation", "pb_ratio")),
            (EXPECTED_26_SECTIONS[3], bool(raw.get("phase2_segments"))),
            (EXPECTED_26_SECTIONS[4], not is_unknown(raw.get("holders", {}).get("shareholding_taxonomy") if isinstance(raw.get("holders"), dict) else None)),
            (EXPECTED_26_SECTIONS[5], _has_metric(metrics, "profitability", "roe") or _has_metric(metrics, "financial_summary", "net_profit")),
            (EXPECTED_26_SECTIONS[6], _has_metric(metrics, "growth", "revenue_cagr_1y")),
            (EXPECTED_26_SECTIONS[7], _has_metric(metrics, "debt_metrics", "debt_to_equity")),
            (EXPECTED_26_SECTIONS[8], _has_metric(metrics, "cash_flow_quality", "cfo_to_pat") or _has_metric(metrics, "cash_flow_quality", "fcf")),
            (EXPECTED_26_SECTIONS[9], _has_metric(metrics, "cash_flow_quality", "fcf")),
            (EXPECTED_26_SECTIONS[10], False),
            (EXPECTED_26_SECTIONS[11], modules.get("red_flags") is not None),
            (EXPECTED_26_SECTIONS[12], False),
            (EXPECTED_26_SECTIONS[13], bool(decision.get("tip_check", {}).get("rows"))),
            (EXPECTED_26_SECTIONS[14], bool(decision.get("watch_next"))),
            (EXPECTED_26_SECTIONS[15], bool(modules.get("company_snapshot"))),
            (EXPECTED_26_SECTIONS[16], False),
            (EXPECTED_26_SECTIONS[17], False),
            (EXPECTED_26_SECTIONS[18], False),
            (EXPECTED_26_SECTIONS[19], isinstance(modules.get("dividends"), list) and bool(modules.get("dividends"))),
            (EXPECTED_26_SECTIONS[20], bool(metrics.get("sector_operating"))),
            (EXPECTED_26_SECTIONS[21], bool(decision.get("group_structure"))),
            (EXPECTED_26_SECTIONS[22], False),
            (EXPECTED_26_SECTIONS[23], bool(modules.get("source_tracking", {}).get("claims"))),
            (EXPECTED_26_SECTIONS[24], consistency.get("status") == "CONSISTENT"),
            (EXPECTED_26_SECTIONS[25], bool(decision.get("research_status"))),
        ]

        completed = [name for name, complete in checks if complete]
        missing = [name for name, complete in checks if not complete]
        completed_count = len(completed)
        missing_count = len(missing)
        badge_text = f"{completed_count}/26 research sections available. {missing_count} sections are unavailable or lack evidence."
        return {
            "completed_count": completed_count,
            "missing_count": missing_count,
            "badge_text": badge_text,
            "completed_sections": completed,
            "missing_sections": missing,
        }
