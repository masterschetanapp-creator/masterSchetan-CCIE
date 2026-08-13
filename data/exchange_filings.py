"""Guarded BSE/NSE filing discovery and primary-document text extraction.

The exchanges do not provide a stable public API contract for unrestricted
automated use. This module therefore treats every response as untrusted input:
it returns only announcements with a real attachment URL and exchange document
identifier, records transport failures, and never substitutes secondary data.
"""

from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:  # Allows offline schema tests without network dependencies.
    requests = None

try:
    from pypdf import PdfReader
except ImportError:  # PDF documents are retained as discovered but not parsed.
    PdfReader = None

from analysis.metric_schema import UNKNOWN


MAX_DOCUMENT_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 250
NSE_HOME_URL = "https://www.nseindia.com/"
NSE_ANNOUNCEMENTS_URL = "https://www.nseindia.com/api/corporate-announcements"
BSE_ANNOUNCEMENTS_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w"
BSE_ATTACHMENT_BASE_URL = "https://api.bseindia.com/DownloadAttachLive/"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; masterSchetan-CCIE/1.0; +https://masterschetan-ccie.streamlit.app/)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
}


def clean_exchange_symbol(symbol: str) -> str:
    """Convert a market symbol such as ``ONGC.NS`` to an exchange symbol."""
    return str(symbol or "").upper().replace(".NS", "").replace(".BO", "").strip()


def _as_iso_date(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return UNKNOWN
    raw = str(value).strip()
    for fmt in (
        "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%d-%b-%Y %H:%M:%S", "%d-%b-%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(raw[:19], fmt).date().isoformat()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return UNKNOWN


def classify_filing_type(title: str) -> str:
    """Classify an exchange announcement without inferring facts from a ticker."""
    normalized = str(title or "").lower()
    if "annual report" in normalized:
        return "ANNUAL_REPORT"
    if "investor presentation" in normalized or "presentation" in normalized:
        return "INVESTOR_PRESENTATION"
    if any(phrase in normalized for phrase in ("transcript", "conference call", "concall", "earnings call")):
        return "EARNINGS_TRANSCRIPT"
    if any(phrase in normalized for phrase in ("financial results", "quarterly results", "quarter ended", "outcome of board meeting")):
        return "QUARTERLY_RESULTS"
    return "COMPANY_REGULATORY_FILING"


def extract_pdf_pages(content: bytes) -> List[Dict[str, Any]]:
    """Extract non-empty PDF page text with the original one-based page number."""
    if PdfReader is None or not content:
        return []
    try:
        reader = PdfReader(BytesIO(content))
    except Exception:
        return []

    pages = []
    for index, pdf_page in enumerate(reader.pages[:MAX_PDF_PAGES], start=1):
        try:
            text = pdf_page.extract_text() or ""
        except Exception:
            continue
        if text.strip():
            pages.append({"page": index, "text": text})
    return pages


def _response_json(response: Any) -> Any:
    try:
        return response.json()
    except Exception:
        return None


def _response_status_ok(response: Any) -> bool:
    status_code = getattr(response, "status_code", 200)
    return isinstance(status_code, int) and 200 <= status_code < 300


def _response_headers(response: Any) -> Dict[str, str]:
    headers = getattr(response, "headers", {}) or {}
    return {str(key).lower(): str(value) for key, value in headers.items()}


def _response_content(response: Any) -> bytes:
    content = getattr(response, "content", b"")
    if isinstance(content, bytes):
        return content
    if isinstance(content, str):
        return content.encode("utf-8", errors="replace")
    return b""


class _ExchangeAdapter:
    """Shared request and document-download behavior for exchange adapters."""

    exchange_name = "EXCHANGE"

    def __init__(self, session: Any = None, timeout_seconds: int = 10):
        self.session = session or (requests.Session() if requests is not None else None)
        self.timeout_seconds = timeout_seconds
        self.errors: List[str] = []

    def _get(self, url: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        if self.session is None:
            self.errors.append(f"{self.exchange_name} filing collection is unavailable because requests is not installed.")
            return None
        try:
            response = self.session.get(url, params=params, headers=DEFAULT_HEADERS, timeout=self.timeout_seconds)
        except Exception as exc:
            self.errors.append(f"{self.exchange_name} request failed: {exc}")
            return None
        if not _response_status_ok(response):
            self.errors.append(f"{self.exchange_name} returned HTTP {getattr(response, 'status_code', 'UNKNOWN')}.")
            return None
        return response

    def download_documents(self, filings: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Download valid source documents and expose text or page-level PDF text."""
        documents: List[Dict[str, Any]] = []
        for filing in filings:
            source_url = str(filing.get("source_url") or "").strip()
            document_id = str(filing.get("document_id") or "").strip()
            if not source_url or not document_id:
                continue
            response = self._get(source_url)
            if response is None:
                continue
            content = _response_content(response)
            if not content or len(content) > MAX_DOCUMENT_BYTES:
                self.errors.append(f"{self.exchange_name} document {document_id} was empty or exceeded the size limit.")
                continue

            headers = _response_headers(response)
            content_type = headers.get("content-type", "").lower()
            document = dict(filing)
            if content.startswith(b"%PDF") or "application/pdf" in content_type or source_url.lower().endswith(".pdf"):
                pages = extract_pdf_pages(content)
                if pages:
                    document["pages"] = pages
                else:
                    document["document_read_status"] = "PDF_TEXT_UNAVAILABLE"
            elif "html" in content_type or source_url.lower().endswith((".html", ".htm")):
                document["html"] = content.decode("utf-8", errors="replace")
            else:
                document["text"] = content.decode("utf-8", errors="replace")
            documents.append(document)
        return documents


class NseFilingAdapter(_ExchangeAdapter):
    """NSE corporate-announcement adapter using the public NSE web endpoint."""

    exchange_name = "NSE"

    def fetch_index(self, symbol: str, max_documents: int = 6) -> List[Dict[str, Any]]:
        exchange_symbol = clean_exchange_symbol(symbol)
        if not exchange_symbol:
            return []

        # NSE generally requires an initial site request to establish cookies.
        self._get(NSE_HOME_URL)
        response = self._get(NSE_ANNOUNCEMENTS_URL, params={"index": "equities", "symbol": exchange_symbol})
        payload = _response_json(response) if response is not None else None
        rows = payload.get("data", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            self.errors.append("NSE returned an announcement payload with no data list.")
            return []

        filings = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            document_id = row.get("an") or row.get("announcement_id") or row.get("id")
            attachment = (
                row.get("attchmntFile") or row.get("attachment") or row.get("attachmentFile")
                or row.get("ATTACHMENTNAME") or row.get("ATTACHMENT")
            )
            if not document_id or not attachment:
                continue
            source_url = str(attachment)
            if not source_url.startswith("http"):
                source_url = urljoin("https://nsearchives.nseindia.com/", source_url.lstrip("/"))
            title = row.get("desc") or row.get("subject") or row.get("headline") or UNKNOWN
            published_date = _as_iso_date(row.get("an_dt") or row.get("broadcast_date") or row.get("date"))
            filings.append({
                "document_id": str(document_id),
                "title": str(title),
                "source_type": classify_filing_type(str(title)),
                "source_url": source_url,
                "published_date": published_date,
                "period_end": UNKNOWN,
                "statement_scope": UNKNOWN,
                "exchange": "NSE",
                "exchange_symbol": exchange_symbol,
            })
        return sorted(filings, key=lambda filing: filing["published_date"] if filing["published_date"] != UNKNOWN else "", reverse=True)[:max_documents]


class BseFilingAdapter(_ExchangeAdapter):
    """BSE corporate-announcement adapter when a verified BSE scrip code is available."""

    exchange_name = "BSE"

    def fetch_index(self, scrip_code: str, max_documents: int = 6, lookback_days: int = 120) -> List[Dict[str, Any]]:
        code = str(scrip_code or "").strip()
        if not code.isdigit():
            return []
        end = date.today()
        start = end - timedelta(days=lookback_days)
        response = self._get(BSE_ANNOUNCEMENTS_URL, params={
            "strCat": "-1",
            "strPrevDate": start.strftime("%Y%m%d"),
            "strScrip": code,
            "strSearch": "P",
            "strToDate": end.strftime("%Y%m%d"),
            "strType": "C",
        })
        payload = _response_json(response) if response is not None else None
        rows = payload.get("Table", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            self.errors.append("BSE returned an announcement payload with no Table list.")
            return []

        filings = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            document_id = row.get("NEWSID") or row.get("NEWS_ID") or row.get("id")
            attachment = row.get("ATTACHMENTNAME") or row.get("ATTACHMENT") or row.get("attachment")
            if not document_id or not attachment:
                continue
            source_url = str(attachment)
            if not source_url.startswith("http"):
                source_url = urljoin(BSE_ATTACHMENT_BASE_URL, source_url.lstrip("/"))
            title = row.get("NEWSSUB") or row.get("SUBJECT") or row.get("HEADLINE") or UNKNOWN
            published_date = _as_iso_date(row.get("NEWS_DT") or row.get("NEWS_DATE") or row.get("DT"))
            filings.append({
                "document_id": str(document_id),
                "title": str(title),
                "source_type": classify_filing_type(str(title)),
                "source_url": source_url,
                "published_date": published_date,
                "period_end": UNKNOWN,
                "statement_scope": UNKNOWN,
                "exchange": "BSE",
                "bse_scrip_code": code,
            })
        return sorted(filings, key=lambda filing: filing["published_date"] if filing["published_date"] != UNKNOWN else "", reverse=True)[:max_documents]


class ExchangeFilingCollector:
    """Collect source documents from exchanges and return the standard evidence pack."""

    def __init__(self, nse_adapter: Optional[NseFilingAdapter] = None, bse_adapter: Optional[BseFilingAdapter] = None):
        self.nse = nse_adapter or NseFilingAdapter()
        self.bse = bse_adapter or BseFilingAdapter()

    def collect(self, symbol: str, *, bse_scrip_code: str = "", max_documents: int = 6) -> Dict[str, Any]:
        nse_filings = self.nse.fetch_index(symbol, max_documents=max_documents)
        bse_filings = self.bse.fetch_index(bse_scrip_code, max_documents=max_documents) if bse_scrip_code else []
        unique_filings: List[Dict[str, Any]] = []
        seen = set()
        for filing in [*nse_filings, *bse_filings]:
            key = (filing.get("exchange"), filing.get("document_id"), filing.get("source_url"))
            if key in seen:
                continue
            seen.add(key)
            unique_filings.append(filing)
        unique_filings.sort(key=lambda filing: filing["published_date"] if filing["published_date"] != UNKNOWN else "", reverse=True)
        unique_filings = unique_filings[:max_documents]
        nse_urls = {filing["source_url"] for filing in unique_filings if filing.get("exchange") == "NSE"}
        bse_urls = {filing["source_url"] for filing in unique_filings if filing.get("exchange") == "BSE"}
        documents = [
            *self.nse.download_documents([filing for filing in unique_filings if filing.get("source_url") in nse_urls]),
            *self.bse.download_documents([filing for filing in unique_filings if filing.get("source_url") in bse_urls]),
        ]
        readable_text_count = sum(bool(document.get("text") or document.get("html") or document.get("pages")) for document in documents)
        return {
            "filing_index": unique_filings,
            "documents": documents,
            "collection": {
                "mode": "EXCHANGE_DIRECT",
                "nse_errors": list(self.nse.errors),
                "bse_errors": list(self.bse.errors),
                "discovered_count": len(unique_filings),
                "downloaded_count": len(documents),
                "readable_text_count": readable_text_count,
            },
        }
