"""Validation gate preventing conflicting figures from reaching report renderers."""

from typing import Any, Dict, List

from analysis.metric_schema import is_unknown


class ReportConsistencyValidator:
    """Compare every view-facing metric with the canonical computed metric object."""

    def validate_dossier_consistency(self, dossier: Dict[str, Any]) -> Dict[str, Any]:
        modules = dossier.get("modules", {}) if isinstance(dossier, dict) else {}
        computed = modules.get("computed_metrics", {})
        decision = dossier.get("decision_support") or modules.get("decision_support", {})
        mismatches: List[str] = []

        if not isinstance(computed, dict) or not isinstance(decision, dict) or not decision:
            return {"status": "BLOCKED", "mismatches": ["Canonical computed metrics or decision support is missing."], "render_allowed": False}

        canonical_type = dossier.get("company_type") or modules.get("company_type")
        if canonical_type != decision.get("company_type"):
            mismatches.append(f"Company type mismatch: dossier={canonical_type!r}, decision={decision.get('company_type')!r}.")

        snapshot = decision.get("metric_snapshot", {})
        if not isinstance(snapshot, dict):
            mismatches.append("Decision support does not expose its canonical metric snapshot.")
        else:
            for metric_name, item in snapshot.items():
                if not isinstance(item, dict):
                    mismatches.append(f"Metric snapshot entry {metric_name!r} is not canonical.")
                    continue
                if "value" not in item or "formatted_string" not in item or "evidence" not in item:
                    mismatches.append(f"Metric snapshot entry {metric_name!r} does not use the metric/evidence schema.")
                evidence = item.get("evidence", {})
                if isinstance(evidence, dict) and evidence.get("source_type") == "SECONDARY_MARKET_DATA" and evidence.get("verification_status") in {"PRIMARY_VERIFIED", "DERIVED_FROM_PRIMARY"}:
                    mismatches.append(f"Metric {metric_name!r} falsely claims primary verification from a secondary source.")

        common_man = modules.get("common_man_report")
        if common_man and common_man is not decision:
            mismatches.append("Common Man view has a separate report payload instead of canonical decision support.")

        source_summary = modules.get("source_tracking", {}).get("summary", {}) if isinstance(modules.get("source_tracking"), dict) else {}
        primary_coverage = source_summary.get("primary_coverage_pct", 0) if isinstance(source_summary, dict) else 0
        research_status = str(decision.get("research_status", "")).lower()
        if not primary_coverage and "primary verified" in research_status:
            mismatches.append("Research status claims primary verification with zero primary evidence coverage.")

        status = "CONSISTENT" if not mismatches else "BLOCKED"
        return {"status": status, "mismatches": mismatches, "render_allowed": not mismatches}
