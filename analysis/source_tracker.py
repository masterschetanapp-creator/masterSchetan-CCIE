import datetime
from typing import Dict, Any, List, Optional

class SourceTracker:
    def __init__(self):
        self.claims: List[Dict[str, Any]] = []
    
    def add_claim(self, claim: str, value: Any, source: str = "Source unavailable", source_type: str = "Unverified Feed",
                  source_date: Optional[str] = None, confidence: int = 0,
                  verification_status: str = "UNVERIFIED",
                  claim_type: str = "FACT",
                  module: str = "general",
                  source_url: Optional[str] = None,
                  source_document_id: Optional[str] = None,
                  page: Optional[int] = None,
                  evidence_snippet: Optional[str] = None,
                  extraction_method: Optional[str] = None) -> Dict[str, Any]:
        """Register a fact with its source, verification status, and claim type."""
        s_lower = str(source or "").lower()
        st_lower = str(source_type or "").lower()
        
        # Enforce source hierarchy: Yahoo / yfinance / Aggregators are strictly secondary market data
        if any(k in s_lower or k in st_lower for k in ["yahoo", "yfinance", "aggregator", "secondary"]):
            source_type = "SECONDARY_MARKET_DATA"
            confidence = min(confidence, 70)
            if verification_status == "PRIMARY_VERIFIED":
                verification_status = "DERIVED_FROM_SECONDARY"
            elif verification_status == "UNVERIFIED":
                verification_status = "SECONDARY_ONLY"

        record = {
            'claim_text': claim,
            'value': value,
            'source': source,
            'source_type': source_type,
            'source_date': source_date,
            'source_url': source_url,
            'source_document_id': source_document_id,
            'page': page,
            'evidence_snippet': evidence_snippet,
            'extraction_method': extraction_method,
            'confidence': confidence,
            'verification_status': verification_status,
            'claim_type': claim_type,
            'module': module,
            'last_checked': datetime.datetime.now().isoformat(),
        }
        self.claims.append(record)
        return record
    
    def get_claims_for_module(self, module: str) -> List[Dict[str, Any]]:
        """Get all tracked claims for a specific module."""
        return [c for c in self.claims if c.get('module') == module]
    
    def get_confidence_summary(self) -> Dict[str, Any]:
        """Overall confidence score for the dossier derived empirically from evidence status."""
        if not self.claims:
            return {'average_confidence': 0, 'total_claims': 0, 'status': 'UNVERIFIED', 'confidence_label': 'UNVERIFIED'}
        
        total = len(self.claims)
        primary_claims = sum(1 for c in self.claims if c.get('verification_status') in ('PRIMARY_VERIFIED', 'DERIVED_FROM_PRIMARY', 'PRIMARY_DOCUMENT_EXTRACTED'))
        secondary_claims = sum(1 for c in self.claims if c.get('verification_status') in ('SECONDARY_ONLY', 'DERIVED_FROM_SECONDARY', 'SINGLE_SECONDARY'))
        unverified_claims = total - (primary_claims + secondary_claims)

        primary_pct = (primary_claims / total) * 100
        secondary_pct = (secondary_claims / total) * 100
        unverified_pct = (unverified_claims / total) * 100

        avg_confidence = sum(c.get('confidence', 0) for c in self.claims) / total

        if primary_pct >= 50:
            status_label = "HIGH (Primary Document Coverage)"
        elif (primary_claims + secondary_claims) / total >= 0.7:
            status_label = "MEDIUM (Secondary Data Coverage)"
        else:
            status_label = "LOW (Unverified / Limited Coverage)"

        return {
            'average_confidence': round(avg_confidence, 1),
            'total_claims': total,
            'primary_coverage_pct': round(primary_pct, 1),
            'secondary_coverage_pct': round(secondary_pct, 1),
            'unverified_pct': round(unverified_pct, 1),
            'status': status_label,
            'confidence_label': status_label
        }
    
    def flag_conflict(self, claim1: Dict[str, Any], claim2: Dict[str, Any], resolution: str) -> Dict[str, Any]:
        """Record a conflict between two sources with resolution."""
        conflict_record = {
            'type': 'conflict',
            'claim1': claim1,
            'claim2': claim2,
            'resolution': resolution,
            'timestamp': datetime.datetime.now().isoformat()
        }
        # In a more advanced implementation, we might store this in a separate conflicts list
        return conflict_record
    
    def to_dict(self) -> Dict[str, Any]:
        """Export all claims as serializable dict."""
        return {
            'claims': self.claims,
            'summary': self.get_confidence_summary()
        }
