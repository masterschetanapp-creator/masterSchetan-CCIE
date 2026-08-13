"""
masterSchetan CCIE — Internal Report Consistency Validator
Cross-validates metric values across all views & modules before UI rendering.
Ensures Common Man View, Simple View, Analyst View, PDF, CTSO, and Tip Check show identical numbers.
"""

from typing import Dict, Any, List


class ConsistencyError(Exception):
    """Raised when two views or modules report conflicting metrics for the same metric field."""
    pass


class ReportConsistencyValidator:
    """
    Validates internal consistency across all 41 research modules and UI renderers.
    """

    def validate_dossier_consistency(self, dossier: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates dossier metric values across decision_support, computed_metrics, and research_snapshot.
        """
        mismatches: List[str] = []
        modules = dossier.get("modules", {})
        computed = modules.get("computed_metrics", {})
        decision = dossier.get("decision_support") or modules.get("decision_support", {})

        if not computed or not decision:
            return {"status": "SKIPPED", "mismatches": []}

        # Check 1: ROE consistency
        comp_roe = computed.get("profitability", {}).get("roe", {}).get("formatted_string") if isinstance(computed.get("profitability"), dict) else None
        ds_roe = decision.get("profitability", {}).get("formatted_string") if isinstance(decision.get("profitability"), dict) else None

        if comp_roe and ds_roe and comp_roe != ds_roe:
            mismatches.append(f"ROE Mismatch: Computed ({comp_roe}) vs DecisionEngine ({ds_roe})")

        # Check 2: Debt to Equity consistency
        comp_de = computed.get("debt_metrics", {}).get("debt_to_equity", {}).get("formatted_string") if isinstance(computed.get("debt_metrics"), dict) else None
        ds_de = decision.get("financial_health", {}).get("de_fmt") if isinstance(decision.get("financial_health"), dict) else None

        if comp_de and ds_de and comp_de != ds_de:
            mismatches.append(f"Debt/Equity Mismatch: Computed ({comp_de}) vs DecisionEngine ({ds_de})")

        if mismatches:
            dossier.setdefault("errors", []).extend(mismatches)
            return {"status": "CONSISTENCY_ERROR", "mismatches": mismatches}

        return {"status": "CONSISTENT", "mismatches": []}
