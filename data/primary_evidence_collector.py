"""Primary-document evidence collection and canonical metric enrichment.

Callers may pass an exchange filing index, downloaded filing documents, or a
manual evidence pack. This collector itself does not discover sources: it
normalizes only records with a real document ID and URL, then returns no claims
when a document is unavailable or cannot be extracted.
"""

from copy import deepcopy
from datetime import datetime
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Optional

from analysis.metric_schema import UNKNOWN, metric
from data.filing_extractors import get_extractor


PRIMARY_SOURCE_TYPES = {
    "COMPANY_REGULATORY_FILING",
    "ANNUAL_REPORT",
    "QUARTERLY_RESULTS",
    "INVESTOR_PRESENTATION",
    "EARNINGS_TRANSCRIPT",
    "CREDIT_RATING_RATIONALE",
    "REGULATORY_BODY",
    "COMPANY_WEBSITE",
}
SOURCE_HIERARCHY = [
    "COMPANY_REGULATORY_FILING", "ANNUAL_REPORT", "QUARTERLY_RESULTS", "INVESTOR_PRESENTATION",
    "EARNINGS_TRANSCRIPT", "CREDIT_RATING_RATIONALE", "REGULATORY_BODY", "COMPANY_WEBSITE",
    "REPUTABLE_MEDIA", "SECONDARY_AGGREGATOR",
]


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: List[str] = []

    def handle_data(self, data: str):
        if data and data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return " ".join(self.parts)


def _normalize_date(value: Any) -> str:
    if not value:
        return UNKNOWN
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return str(value)


def _primary_extraction_status(source_type: str, source_url: str, document_id: str) -> str:
    if source_type in PRIMARY_SOURCE_TYPES and source_url and document_id:
        return "PRIMARY_DOCUMENT_EXTRACTED"
    return "UNVERIFIED"


def create_evidence_claim(
    metric: str,
    value: Any,
    unit: str = "",
    period: str = "",
    source_type: str = "SECONDARY_AGGREGATOR",
    source_url: str = "",
    published_date: str = "",
    page: Optional[int] = None,
    verification_status: str = "UNVERIFIED",
    *,
    period_end: str = "",
    reporting_period: str = UNKNOWN,
    statement_scope: str = UNKNOWN,
    document_id: str = "",
    document_title: str = "",
    evidence_snippet: str = "",
    extraction_method: str = "",
) -> Dict[str, Any]:
    """Create a serialisable claim with enough provenance for an audit trail."""
    normalized_source_type = source_type if source_type in SOURCE_HIERARCHY else "SECONDARY_AGGREGATOR"
    status = verification_status or "UNVERIFIED"
    if status == "UNVERIFIED":
        status = _primary_extraction_status(normalized_source_type, source_url, document_id)
    return {
        "metric": metric,
        "value": value,
        "unit": unit or UNKNOWN,
        "period": period or period_end or UNKNOWN,
        "period_end": period_end or period or UNKNOWN,
        "reporting_period": reporting_period or UNKNOWN,
        "statement_scope": statement_scope or UNKNOWN,
        "source_type": normalized_source_type,
        "source_url": source_url or UNKNOWN,
        "source_document_id": document_id or UNKNOWN,
        "document_title": document_title or UNKNOWN,
        "published_date": _normalize_date(published_date),
        "page": page,
        "verification_status": status,
        "evidence_snippet": evidence_snippet or UNKNOWN,
        "extraction_method": extraction_method or UNKNOWN,
        "timestamp": datetime.now().isoformat(),
    }


def _document_text(document: Dict[str, Any]) -> str:
    text = document.get("text") or document.get("content") or ""
    if text:
        return str(text)
    html = document.get("html") or ""
    if not html:
        return ""
    parser = _TextExtractor()
    parser.feed(str(html))
    return parser.text()


def _document_pages(document: Dict[str, Any]) -> List[tuple[Optional[int], str]]:
    """Return page-specific text when available, otherwise the document text."""
    pages = document.get("pages")
    if isinstance(pages, list):
        extracted_pages = []
        for page in pages:
            if not isinstance(page, dict):
                continue
            text = page.get("text") or page.get("content") or ""
            if str(text).strip():
                page_number = page.get("page")
                extracted_pages.append((page_number if isinstance(page_number, int) else None, str(text)))
        if extracted_pages:
            return extracted_pages
    return [(document.get("page"), _document_text(document))]


def _claim_sort_key(claim: Dict[str, Any]) -> tuple[str, str]:
    period_end = str(claim.get("period_end", ""))
    published_date = str(claim.get("published_date", ""))
    return (
        "" if period_end == UNKNOWN else period_end,
        "" if published_date == UNKNOWN else published_date,
    )


def select_latest_claims(claims: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retain the newest claim for each metric and statement scope."""
    latest: Dict[tuple[str, str], Dict[str, Any]] = {}
    for claim in claims:
        if not isinstance(claim, dict) or not claim.get("metric"):
            continue
        key = (str(claim["metric"]), str(claim.get("statement_scope", UNKNOWN)))
        if key not in latest or _claim_sort_key(claim) > _claim_sort_key(latest[key]):
            latest[key] = claim
    return list(latest.values())


def merge_primary_claims_into_metrics(computed_metrics: Dict[str, Any], claims: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Add current primary-document sector metrics without overwriting calculations.

    Financial statement metrics calculated from secondary data remain separately
    labelled. Primary operating claims are added under ``sector_operating`` and
    can satisfy sector-specific evidence requirements in the decision engine.
    """
    enriched = deepcopy(computed_metrics) if isinstance(computed_metrics, dict) else {}
    sector_metrics = enriched.setdefault("sector_operating", {})
    primary_claims = [
        claim for claim in select_latest_claims(claims)
        if claim.get("source_type") in PRIMARY_SOURCE_TYPES
        and claim.get("verification_status") == "PRIMARY_DOCUMENT_EXTRACTED"
    ]
    for claim in primary_claims:
        raw_value = claim.get("value")
        unit = claim.get("unit", UNKNOWN)
        formatted = f"{raw_value:g} {unit}" if isinstance(raw_value, (int, float)) else str(raw_value)
        item = metric(
            raw_value,
            formatted_string=formatted,
            explanation=f"Extracted from {claim.get('document_title', UNKNOWN)}.",
            reporting_period=claim.get("reporting_period", UNKNOWN),
            statement_scope=claim.get("statement_scope", UNKNOWN),
            period_end=claim.get("period_end", UNKNOWN),
            source_type=claim.get("source_type", UNKNOWN),
            verification_status=claim.get("verification_status", "UNVERIFIED"),
        )
        item["evidence"].update({
            "source_url": claim.get("source_url", UNKNOWN),
            "source_document_id": claim.get("source_document_id", UNKNOWN),
            "page": claim.get("page"),
            "evidence_snippet": claim.get("evidence_snippet", UNKNOWN),
            "extraction_method": claim.get("extraction_method", UNKNOWN),
        })
        sector_metrics[claim["metric"]] = item
    enriched["primary_evidence"] = {
        "claim_count": len(primary_claims),
        "latest_claims": primary_claims,
    }
    return enriched


def build_uploaded_evidence_pack(
    content: str,
    *,
    source_type: str,
    source_url: str,
    document_id: str,
    document_title: str = "",
    period_end: str = "",
    reporting_period: str = UNKNOWN,
    statement_scope: str = UNKNOWN,
    published_date: str = "",
    page: Optional[int] = None,
    content_format: str = "text",
) -> Dict[str, List[Dict[str, Any]]]:
    """Build a validated evidence pack from one user-supplied filing document.

    A local upload is not primary evidence by itself. It becomes eligible only
    when the user supplies a recognised primary-source category, public source
    URL, and the filing's genuine identifier. The caller must leave the pack
    empty when any of those items is unavailable.
    """
    normalized_source_type = str(source_type or "").upper()
    normalized_url = str(source_url or "").strip()
    normalized_document_id = str(document_id or "").strip()
    normalized_content = str(content or "").strip()
    if (
        normalized_source_type not in PRIMARY_SOURCE_TYPES
        or not normalized_url
        or not normalized_document_id
        or not normalized_content
    ):
        return {"filing_index": [], "documents": []}

    document = {
        "document_id": normalized_document_id,
        "title": document_title or UNKNOWN,
        "source_type": normalized_source_type,
        "source_url": normalized_url,
        "published_date": published_date or UNKNOWN,
        "period_end": period_end or UNKNOWN,
        "reporting_period": reporting_period or UNKNOWN,
        "statement_scope": statement_scope or UNKNOWN,
        "page": page,
        "html" if str(content_format).lower() == "html" else "text": normalized_content,
    }
    filing_index = {
        "document_id": normalized_document_id,
        "title": document_title or UNKNOWN,
        "source_type": normalized_source_type,
        "source_url": normalized_url,
        "published_date": published_date or UNKNOWN,
        "period_end": period_end or UNKNOWN,
        "statement_scope": statement_scope or UNKNOWN,
    }
    return {"filing_index": [filing_index], "documents": [document]}


class PrimaryEvidenceCollector:
    """Ingest approved primary documents and extract reusable structured claims."""

    def __init__(self, symbol: str, company_name: str, company_type: str = UNKNOWN):
        self.symbol = str(symbol or "").upper()
        self.company_name = company_name or UNKNOWN
        self.company_type = company_type or UNKNOWN
        self.extracted_claims: List[Dict[str, Any]] = []
        self.discovered_sources: List[Dict[str, Any]] = []
        self.processed_document_ids: set[str] = set()

    def discover_primary_sources(self, filing_index: Any = None) -> List[Dict[str, Any]]:
        """Normalize a caller-supplied filing index; do not invent a discovery result."""
        entries = filing_index.get("filings", []) if isinstance(filing_index, dict) else filing_index
        if not isinstance(entries, list):
            return []
        discovered = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            source_type = entry.get("source_type", "")
            source_url = entry.get("source_url") or entry.get("url")
            document_id = entry.get("document_id") or entry.get("id")
            if source_type not in PRIMARY_SOURCE_TYPES or not source_url or not document_id:
                continue
            discovered.append({
                "document_id": str(document_id),
                "title": entry.get("title") or UNKNOWN,
                "source_type": source_type,
                "source_url": str(source_url),
                "published_date": _normalize_date(entry.get("published_date")),
                "period_end": _normalize_date(entry.get("period_end")),
                "statement_scope": entry.get("statement_scope", UNKNOWN),
                "status": "DISCOVERED",
            })
        self.discovered_sources = discovered
        return discovered

    def extract_structured_claims(self, raw_document_data: Any = None) -> List[Dict[str, Any]]:
        """Extract only labelled facts from supplied primary-document text."""
        documents = raw_document_data.get("documents", []) if isinstance(raw_document_data, dict) else raw_document_data
        if not isinstance(documents, list):
            return list(self.extracted_claims)
        extractor = get_extractor(self.company_type)

        claims: List[Dict[str, Any]] = []
        for document in documents:
            if not isinstance(document, dict):
                continue
            source_type = document.get("source_type", "")
            source_url = document.get("source_url") or document.get("url") or ""
            document_id = str(document.get("document_id") or document.get("id") or "")
            if source_type not in PRIMARY_SOURCE_TYPES or not source_url or not document_id:
                continue
            self.processed_document_ids.add(document_id)
            if extractor is None:
                continue
            for page_number, text in _document_pages(document):
                for extracted in extractor.extract(text):
                    claims.append(create_evidence_claim(
                        metric=extracted["metric"],
                        value=extracted["value"],
                        unit=extracted["unit"],
                        source_type=source_type,
                        source_url=source_url,
                        published_date=document.get("published_date", ""),
                        page=page_number if page_number is not None else document.get("page"),
                        period_end=document.get("period_end", ""),
                        reporting_period=document.get("reporting_period", UNKNOWN),
                        statement_scope=document.get("statement_scope", UNKNOWN),
                        document_id=document_id,
                        document_title=document.get("title", ""),
                        evidence_snippet=extracted["evidence_snippet"],
                        extraction_method=extracted["extraction_method"],
                    ))
        self.extracted_claims = select_latest_claims([*self.extracted_claims, *claims])
        return list(self.extracted_claims)

    def to_dict(self) -> Dict[str, Any]:
        """Return the collector result for the dossier and source tracker."""
        return {
            "symbol": self.symbol,
            "company_name": self.company_name,
            "company_type": self.company_type,
            "discovered_sources": self.discovered_sources,
            "claims": self.extracted_claims,
            "primary_document_count": len(
                self.processed_document_ids | {source.get("document_id") for source in self.discovered_sources}
            ),
        }
