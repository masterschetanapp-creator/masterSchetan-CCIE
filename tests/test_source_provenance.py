from analysis.source_tracker import SourceTracker

def test_source_provenance_defaults():
    tracker = SourceTracker()
    claim = tracker.add_claim(
        claim="Test Claim",
        value=100,
        source="Test Source",
        source_type="Unverified Feed"
    )
    assert claim["verification_status"] == "UNVERIFIED"
    
    summary = tracker.get_confidence_summary()
    assert "status" in summary
    assert "confidence_label" in summary

if __name__ == "__main__":
    test_source_provenance_defaults()
    print("test_source_provenance PASSED")
