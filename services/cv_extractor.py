"""Text extraction from PDF / DOCX files (uploaded or downloaded from a link)."""
import io
import ipaddress
import socket
import urllib.parse
import urllib.request

MAX_BYTES = 5 * 1024 * 1024
MIN_CHARS = 80
ALLOWED = (".pdf", ".docx")


class CVError(Exception):
    """User-facing problem with the CV file."""


def _pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise CVError("This PDF is password-protected. Please upload an unlocked copy.")
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except CVError:
        raise
    except (PyPdfError, Exception) as exc:  # corrupt files raise many different errors
        raise CVError("Could not read this PDF. The file may be corrupted.") from exc


def _docx_text(data: bytes) -> str:
    from docx import Document
    try:
        doc = Document(io.BytesIO(data))
    except Exception as exc:
        raise CVError("Could not read this DOCX. The file may be corrupted.") from exc
    lines = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            lines.append(" | ".join(c.text.strip() for c in row.cells if c.text.strip()))
    return "\n".join(lines)


def extract_text(data: bytes, filename: str) -> str:
    """Validate the file and return cleaned text. Raises CVError with a friendly message."""
    name = (filename or "").lower()
    if not name.endswith(ALLOWED):
        raise CVError("Unsupported file type. Please upload a PDF or DOCX file.")
    if len(data) > MAX_BYTES:
        raise CVError(f"File is too large. The maximum size is {MAX_BYTES // (1024 * 1024)} MB.")
    if not data:
        raise CVError("The file is empty.")
    text = _pdf_text(data) if name.endswith(".pdf") else _docx_text(data)
    text = "\n".join(line.rstrip() for line in text.replace("\r", "\n").replace("\x00", "").split("\n"))
    if len(text.strip()) < MIN_CHARS:
        raise CVError("Very little text could be extracted. Scanned or image-only CVs are not supported yet - "
                      "please upload a text-based PDF or a DOCX file.")
    return text.strip()


def _check_public_host(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise CVError("Could not resolve that link.") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise CVError("That link points to a private address and cannot be used.")


def fetch_from_link(url: str) -> tuple:
    """Download a PDF/DOCX from a public link. Returns (bytes, filename)."""
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise CVError("Enter a valid link that starts with http:// or https://")
    _check_public_host(parsed.hostname)
    req = urllib.request.Request(url.strip(), headers={"User-Agent": "AI-Smart-Job-Matcher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 - scheme validated above
            data = resp.read(MAX_BYTES + 1)
    except Exception as exc:
        raise CVError("Could not download the file from that link.") from exc
    if len(data) > MAX_BYTES:
        raise CVError("The linked file is too large (max 5 MB).")
    base = parsed.path.rsplit("/", 1)[-1] or "cv"
    if data.startswith(b"%PDF"):
        ext = ".pdf"
    elif data.startswith(b"PK"):
        ext = ".docx"
    else:
        raise CVError("The link did not return a PDF or DOCX file. Use a direct download link.")
    return data, base if base.lower().endswith(ext) else base + ext
