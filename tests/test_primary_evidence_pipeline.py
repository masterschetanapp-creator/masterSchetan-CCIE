"""Primary-document extraction tests using an offline upstream E&P filing fixture."""

from pathlib import Path

from analysis.decision_engine import DecisionEngine
from analysis.metric_schema import metric
from analysis.source_tracker import SourceTracker
from data.primary_evidence_collector import (
    PrimaryEvidenceCollector,
    build_uploaded_evidence_pack,
    create_evidence_claim,
    merge_primary_claims_into_metrics,
    select_latest_claims,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "upstream_ep_primary_filing.txt"


def _primary_document(period_end: str = "2026-06-30"):
    return {
        "document_id": f"fixture-upstream-{period_end}",
        "title": "Upstream E&P quarterly results fixture",
        "source_type": "QUARTERLY_RESULTS",
        "source_url": "https://primary.example.test/filings/upstream-results",
        "published_date": "2026-08-01",
        "period_end": period_end,
        "reporting_period": "latest_quarter",
        "statement_scope": "STANDALONE",
        "page": 4,
        "text": FIXTURE_PATH.read_text(encoding="utf-8"),
    }


def test_primary_upstream_filing_extraction_has_document_provenance():
    collector = PrimaryEvidenceCollector("TEST.NS", "Generic Upstream Producer", "OIL_GAS_E&P")
    assert collector.discover_primary_sources() == []

    claims = collector.extract_structured_claims([_primary_document()])
    extracted_names = {claim["metric"] for claim in claims}
    assert {
        "crude_oil_production_mmt", "natural_gas_production_bcm", "total_boe_production",
        "crude_realisation_usd_per_bbl", "gas_realisation_usd_per_mmbtu", "reserve_replacement_ratio",
        "lifting_cost_usd_per_bbl", "exploration_capex_cr", "development_capex_cr", "discoveries",
    } <= extracted_names
    for claim in claims:
        assert claim["verification_status"] == "PRIMARY_DOCUMENT_EXTRACTED"
        assert claim["source_url"].startswith("https://primary.example.test/")
        assert claim["statement_scope"] == "STANDALONE"
        assert claim["page"] == 4
        assert claim["evidence_snippet"] != "UNKNOWN"


def test_primary_claims_require_a_real_document_identifier_and_url():
    collector = PrimaryEvidenceCollector("TEST.NS", "Generic Upstream Producer", "OIL_GAS_E&P")
    document = _primary_document()
    document.pop("source_url")
    assert collector.extract_structured_claims([document]) == []


def test_processed_primary_document_is_counted_even_without_a_supported_extraction():
    collector = PrimaryEvidenceCollector("TEST.NS", "Generic Industrial", "INDUSTRIAL")
    document = _primary_document()
    assert collector.extract_structured_claims([document]) == []
    assert collector.to_dict()["primary_document_count"] == 1


def test_uploaded_evidence_pack_requires_primary_metadata_before_it_can_be_extracted():
    content = FIXTURE_PATH.read_text(encoding="utf-8")
    rejected = build_uploaded_evidence_pack(
        content,
        source_type="QUARTERLY_RESULTS",
        source_url="",
        document_id="",
    )
    assert rejected == {"filing_index": [], "documents": []}

    accepted = build_uploaded_evidence_pack(
        content,
        source_type="QUARTERLY_RESULTS",
        source_url="https://primary.example.test/filings/upstream-results",
        document_id="announcement-123",
        document_title="Quarterly Results",
        period_end="2026-06-30",
        reporting_period="latest_quarter",
        statement_scope="STANDALONE",
    )
    collector = PrimaryEvidenceCollector("TEST.NS", "Generic Upstream Producer", "OIL_GAS_E&P")
    assert len(collector.discover_primary_sources(accepted["filing_index"])) == 1
    assert len(collector.extract_structured_claims(accepted["documents"])) == 10


def test_latest_primary_claim_wins_within_the_same_scope():
    older = create_evidence_claim(
        "crude_oil_production_mmt", 4.0, unit="MMT", source_type="QUARTERLY_RESULTS",
        source_url="https://primary.example.test/old", document_id="old", period_end="2026-03-31",
        statement_scope="STANDALONE",
    )
    latest = create_evidence_claim(
        "crude_oil_production_mmt", 4.25, unit="MMT", source_type="QUARTERLY_RESULTS",
        source_url="https://primary.example.test/latest", document_id="latest", period_end="2026-06-30",
        statement_scope="STANDALONE",
    )
    selected = select_latest_claims([older, latest])
    assert len(selected) == 1
    assert selected[0]["value"] == 4.25


def test_primary_sector_metrics_enrich_e_and_p_coverage_without_overwriting_financials():
    collector = PrimaryEvidenceCollector("TEST.NS", "Generic Upstream Producer", "OIL_GAS_E&P")
    primary_claims = collector.extract_structured_claims([_primary_document()])
    secondary_financials = {
        "financial_summary": {"revenue": metric(1000, "1,000 Cr"), "net_profit": metric(100, "100 Cr")},
        "debt_metrics": {"debt_to_equity": metric(0.3, "0.30x")},
        "cash_flow_quality": {"cfo_to_pat": metric(1.1, "1.10x")},
        "valuation": {"pe_ratio": metric(7.0, "7.00")},
    }
    enriched = merge_primary_claims_into_metrics(secondary_financials, primary_claims)
    assert enriched["financial_summary"]["revenue"]["evidence"]["source_type"] == "SECONDARY_MARKET_DATA"
    production = enriched["sector_operating"]["crude_oil_production_mmt"]
    assert production["value"] == 4.25
    assert production["evidence"]["source_type"] == "QUARTERLY_RESULTS"
    assert production["evidence"]["statement_scope"] == "STANDALONE"

    decision = DecisionEngine().build({}, "OIL_GAS_E&P", enriched, {}, [], [], [])
    assert decision["coverage"]["confidence"] == "HIGH"
    assert decision["valuation"]["status"] == "CYCLE_SENSITIVE"
    assert decision["metric_snapshot"]["production_volume"]["evidence"]["source_type"] == "QUARTERLY_RESULTS"


def test_source_tracker_counts_primary_documents_without_relabelling_secondary_claims():
    tracker = SourceTracker()
    tracker.add_claim(
        "Primary production figure", 4.25, source="Quarterly results fixture", source_type="QUARTERLY_RESULTS",
        verification_status="PRIMARY_DOCUMENT_EXTRACTED", module="primary_evidence",
        source_url="https://primary.example.test/filings/upstream-results", source_document_id="fixture",
    )
    tracker.add_claim(
        "Secondary market price", 100, source="Yahoo Finance", source_type="Data aggregator",
        verification_status="PRIMARY_VERIFIED", module="stock_data",
    )
    claims = tracker.to_dict()["claims"]
    assert claims[1]["verification_status"] == "DERIVED_FROM_SECONDARY"
    summary = tracker.get_confidence_summary()
    assert summary["primary_coverage_pct"] == 50.0
    assert summary["secondary_coverage_pct"] == 50.0
