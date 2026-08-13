"""Deterministic extractors for text obtained from primary company documents."""

import re
from typing import Any, Dict, List


_NUMBER = r"(?P<value>\d[\d,]*(?:\.\d+)?)"


class UpstreamOilGasExtractor:
    """Extract common E&P operating metrics without referring to a company name.

    The extractor intentionally accepts only labelled values from the supplied
    document text. It does not infer a value from a ticker, a sector label, or
    a narrative sentence. A parser match is a primary-document extraction, not
    an audited verification of the underlying value.
    """

    metric_patterns: Dict[str, Dict[str, Any]] = {
        "crude_oil_production_mmt": {
            "unit": "MMT",
            "patterns": [
                rf"\bcrude\s+(?:oil\s+)?production\s*(?:\([^)]*\))?\s*[:\-]?\s*{_NUMBER}\s*(?:MMT|million\s+metric\s+tonnes?)\b",
            ],
        },
        "natural_gas_production_bcm": {
            "unit": "BCM",
            "patterns": [
                rf"\bnatural\s+gas\s+production\s*(?:\([^)]*\))?\s*[:\-]?\s*{_NUMBER}\s*(?:BCM|billion\s+cubic\s+met(?:er|re)s?)\b",
            ],
        },
        "total_boe_production": {
            "unit": "BOE",
            "patterns": [
                rf"\b(?:total\s+)?(?:oil\s+and\s+gas\s+)?production\s*(?:\([^)]*\))?\s*[:\-]?\s*{_NUMBER}\s*(?:MBOE|MMBOE|BOE)\b",
            ],
        },
        "crude_realisation_usd_per_bbl": {
            "unit": "USD/bbl",
            "patterns": [
                rf"\b(?:net\s+)?crude\s+(?:oil\s+)?realisation\s*(?:\([^)]*\))?\s*[:\-]?\s*\$?\s*{_NUMBER}\s*(?:USD\s*/\s*bbl|\$/\s*bbl|per\s+barrel)\b",
            ],
        },
        "gas_realisation_usd_per_mmbtu": {
            "unit": "USD/mmbtu",
            "patterns": [
                rf"\b(?:net\s+)?gas\s+realisation\s*(?:\([^)]*\))?\s*[:\-]?\s*\$?\s*{_NUMBER}\s*(?:USD\s*/\s*mmbtu|\$/\s*mmbtu|per\s+mmbtu)\b",
            ],
        },
        "reserve_replacement_ratio": {
            "unit": "x",
            "patterns": [
                rf"\b(?:reserve\s+replacement\s+ratio|RRR)\s*(?:\([^)]*\))?\s*[:\-]?\s*{_NUMBER}\s*(?:x|times)?\b",
            ],
        },
        "lifting_cost_usd_per_bbl": {
            "unit": "USD/bbl",
            "patterns": [
                rf"\blifting\s+cost\s*(?:\([^)]*\))?\s*[:\-]?\s*\$?\s*{_NUMBER}\s*(?:USD\s*/\s*bbl|\$/\s*bbl|per\s+barrel)\b",
            ],
        },
        "exploration_capex_cr": {
            "unit": "INR Cr",
            "patterns": [
                rf"\bexploration\s+capex\s*(?:\([^)]*\))?\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*{_NUMBER}\s*(?:Cr|crore)\b",
            ],
        },
        "development_capex_cr": {
            "unit": "INR Cr",
            "patterns": [
                rf"\bdevelopment\s+capex\s*(?:\([^)]*\))?\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*{_NUMBER}\s*(?:Cr|crore)\b",
            ],
        },
        "discoveries": {
            "unit": "count",
            "patterns": [
                rf"\b(?:new\s+)?discoveries\s*(?:\([^)]*\))?\s*[:\-]?\s*{_NUMBER}\b",
            ],
        },
    }

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Return at most one labelled value for each standardised metric."""
        if not isinstance(text, str) or not text.strip():
            return []

        extracted: List[Dict[str, Any]] = []
        for metric, definition in self.metric_patterns.items():
            for pattern in definition["patterns"]:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if not match:
                    continue
                value = float(match.group("value").replace(",", ""))
                start = max(0, match.start() - 120)
                end = min(len(text), match.end() + 120)
                extracted.append({
                    "metric": metric,
                    "value": value,
                    "unit": definition["unit"],
                    "evidence_snippet": " ".join(text[start:end].split()),
                    "extraction_method": "LABELLED_TEXT_REGEX",
                })
                break
        return extracted


def get_extractor(company_type: str):
    """Return a reusable extractor for a canonical company type, if available."""
    if str(company_type or "").upper() in {"OIL_GAS_E&P", "OIL_GAS_INTEGRATED"}:
        return UpstreamOilGasExtractor()
    return None
