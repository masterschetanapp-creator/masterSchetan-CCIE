import datetime
from typing import Dict, Any, List, Optional

class SourceTracker:
    def __init__(self):
        self.claims: List[Dict[str, Any]] = []
    
    def add_claim(self, claim: str, value: Any, source: str, source_type: str,
                  source_date: Optional[str] = None, confidence: int = 90,
                  verification_status: str = "PRIMARY_VERIFIED",
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
        """Overall confidence score for the dossier."""
        if not self.claims:
            return {'average_confidence': 0, 'total_claims': 0}
        
        avg_confidence = sum(c.get('confidence', 0) for c in self.claims) / len(self.claims)
        
        return {
            'average_confidence': avg_confidence,
            'total_claims': len(self.claims),
            'status': 'High' if avg_confidence >= 85 else ('Medium' if avg_confidence >= 70 else 'Low')
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
