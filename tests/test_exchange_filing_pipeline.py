"""Offline regression tests for guarded NSE/BSE filing collection."""

from data import exchange_filings
from data.exchange_filings import BseFilingAdapter, ExchangeFilingCollector, NseFilingAdapter, extract_pdf_pages
from data.primary_evidence_collector import PrimaryEvidenceCollector


class FakeResponse:
    def __init__(self, *, payload=None, content=b"", headers=None, status_code=200):
        self._payload = payload
        self.content = content
        self.headers = headers or {}
        self.status_code = status_code

    def json(self):
        if self._payload is None:
            raise ValueError("No JSON payload")
        return self._payload


class FakeNseSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, params))
        if url == exchange_filings.NSE_HOME_URL:
            return FakeResponse(content=b"home")
        if url == exchange_filings.NSE_ANNOUNCEMENTS_URL:
            return FakeResponse(payload={"data": [
                {
                    "an": "older-1",
                    "attchmntFile": "corporate/ONGC/older.txt",
                    "desc": "Financial Results for quarter ended March 2026",
                    "an_dt": "20-Apr-2026 10:00:00",
                },
                {
                    "an": "latest-2",
                    "attchmntFile": "corporate/ONGC/latest.txt",
                    "desc": "Financial Results for quarter ended June 2026",
                    "an_dt": "10-Aug-2026 10:00:00",
                },
                {
                    "attchmntFile": "corporate/ONGC/invalid.txt",
                    "desc": "Financial Results",
                    "an_dt": "11-Aug-2026 10:00:00",
                },
            ]})
        if url.endswith("latest.txt"):
            return FakeResponse(
                content=b"Crude oil production: 4.25 MMT\nReserve Replacement Ratio: 1.12x",
                headers={"content-type": "text/plain"},
            )
        if url.endswith("older.txt"):
            return FakeResponse(content=b"Crude oil production: 4.00 MMT", headers={"content-type": "text/plain"})
        return FakeResponse(status_code=404)


class FakeBseSession:
    def get(self, url, params=None, headers=None, timeout=None):
        assert params["strScrip"] == "500312"
        return FakeResponse(payload={"Table": [
            {
                "NEWSID": "bse-22",
                "ATTACHMENTNAME": "bse-result.pdf",
                "NEWSSUB": "Annual Report 2026",
                "NEWS_DT": "11/08/2026 15:30:00",
            }
        ]})


def test_nse_adapter_keeps_only_real_announcement_ids_and_sorts_latest_first():
    adapter = NseFilingAdapter(session=FakeNseSession())
    filings = adapter.fetch_index("ONGC.NS")
    assert [filing["document_id"] for filing in filings] == ["latest-2", "older-1"]
    assert filings[0]["source_url"] == "https://nsearchives.nseindia.com/corporate/ONGC/latest.txt"
    assert filings[0]["source_type"] == "QUARTERLY_RESULTS"
    assert filings[0]["published_date"] == "2026-08-10"


def test_bse_adapter_requires_a_verified_scrip_code_and_preserves_attachment_url():
    adapter = BseFilingAdapter(session=FakeBseSession())
    assert adapter.fetch_index("") == []
    filings = adapter.fetch_index("500312")
    assert len(filings) == 1
    assert filings[0]["document_id"] == "bse-22"
    assert filings[0]["source_url"] == "https://api.bseindia.com/DownloadAttachLive/bse-result.pdf"
    assert filings[0]["source_type"] == "ANNUAL_REPORT"


def test_exchange_collector_downloads_primary_text_and_feeds_the_existing_ep_extractor():
    collector = ExchangeFilingCollector(nse_adapter=NseFilingAdapter(session=FakeNseSession()), bse_adapter=BseFilingAdapter(session=FakeBseSession()))
    evidence_pack = collector.collect("ONGC.NS", max_documents=1)
    assert evidence_pack["collection"]["mode"] == "EXCHANGE_DIRECT"
    assert evidence_pack["collection"]["discovered_count"] == 1
    assert evidence_pack["collection"]["downloaded_count"] == 1
    assert evidence_pack["collection"]["readable_text_count"] == 1
    assert evidence_pack["documents"][0]["document_id"] == "latest-2"

    primary = PrimaryEvidenceCollector("ONGC.NS", "Generic Upstream Producer", "OIL_GAS_E&P")
    claims = primary.extract_structured_claims(evidence_pack["documents"])
    crude_claim = next(claim for claim in claims if claim["metric"] == "crude_oil_production_mmt")
    assert crude_claim["value"] == 4.25
    assert crude_claim["verification_status"] == "PRIMARY_DOCUMENT_EXTRACTED"
    assert crude_claim["source_document_id"] == "latest-2"


def test_pdf_page_extraction_preserves_page_numbers_without_claiming_unreadable_documents():
    class FakePage:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class FakeReader:
        def __init__(self, _stream):
            self.pages = [FakePage(""), FakePage("Crude oil production: 4.25 MMT")]

    original_reader = exchange_filings.PdfReader
    exchange_filings.PdfReader = FakeReader
    try:
        pages = extract_pdf_pages(b"%PDF-test")
    finally:
        exchange_filings.PdfReader = original_reader
    assert pages == [{"page": 2, "text": "Crude oil production: 4.25 MMT"}]

    document = {
        "document_id": "pdf-fixture",
        "title": "Quarterly Results",
        "source_type": "QUARTERLY_RESULTS",
        "source_url": "https://primary.example.test/filing.pdf",
        "published_date": "2026-08-01",
        "period_end": "2026-06-30",
        "statement_scope": "STANDALONE",
        "pages": pages,
    }
    claims = PrimaryEvidenceCollector("TEST.NS", "Generic Upstream Producer", "OIL_GAS_E&P").extract_structured_claims([document])
    assert claims[0]["page"] == 2
