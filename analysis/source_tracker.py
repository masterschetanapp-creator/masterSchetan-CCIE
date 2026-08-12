import datetime
from typing import Dict, Any, List, Optional

class SourceTracker:
    def __init__(self):
        self.claims: List[Dict[str, Any]] = []
    
    def add_claim(self, claim: str, value: Any, source: str = "Source unavailable", source_type: str = "Unverified Feed",
                  source_date: Optional[str] = None, confidence: int = 0,
                  verification_status: str = "UNVERIFIED",
                  claim_type: str = "FACT",
                  module: str = "general") -> Dict[str, Any]:
        """Register a fact with its source, verification status, and claim type."""
        record = {
            'claim_text': claim,
            'value': value,
            'source': source,
            'source_type': source_type,
            'source_date': source_date,
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
        primary_claims = sum(1 for c in self.claims if c.get('verification_status') in ('PRIMARY_VERIFIED', 'DERIVED_FROM_PRIMARY'))
        secondary_claims = sum(1 for c in self.claims if c.get('verification_status') in ('SECONDARY_ONLY', 'DERIVED_FROM_SECONDARY', 'SINGLE_SECONDARY'))
        unverified_claims = total - (primary_claims + secondary_claims)

        primary_pct = (primary_claims / total) * 100
        secondary_pct = (secondary_claims / total) * 100
        unverified_pct = (unverified_claims / total) * 100

        avg_confidence = sum(c.get('confidence', 0) for c in self.claims) / total

        if primary_pct >= 50:
            status_label = "HIGH (Primary Exchange / Filing Verified)"
        elif (primary_claims + secondary_claims) / total >= 0.7:
            status_label = "MEDIUM (Secondary Aggregator Verified)"
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
