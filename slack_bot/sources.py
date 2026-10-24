"""Turn the modal's reference links and uploaded files into local files the agent can read.

The bot does all network access here; the agent itself never gets a network
tool, so a fetched page can only ever be *read* as input. Everything lands in
<run>/attachments/ and is listed in input.md.

Supported:
- Slack uploads (PDF, images, text formats, DOCX -> text via macOS textutil)
- Confluence Cloud pages (needs CONFLUENCE_EMAIL + CONFLUENCE_API_TOKEN): page URLs, ?pageId= URLs and
  /wiki/x/<code> short links, read through the REST API v2 as rendered HTML -> text, plus up to 5 direct child pages
- Figma links (needs FIGMA_TOKEN): linked frame, or the first page's top-level screens (up to 12), exported as PNG
- Google Docs shared as "anyone with the link" (exported as text)
- Any other public http(s) URL: HTML -> text, PDF / images / text kept as files
Private pages (Confluence, Notion, Google Docs not shared publicly, ...) are
reported back as "couldn't read - upload the file instead".
"""

from __future__ import annotations

import base64
import functools
import ipaddress
import os
import json
import re
import shutil
import socket
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

MAX_LINKS = 10
MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
MAX_FIGMA_FRAMES = 12  # a typical flow (cover + ~10 screens); each frame is one image for the agent
HTTP_TIMEOUT = 30
MIN_PAGE_TEXT = 200  # less readable text than this usually means a login wall or a JavaScript-only page

UPLOAD_FILETYPES = ["pdf", "png", "jpg", "jpeg", "gif", "webp", "md", "txt", "csv", "json", "yaml", "yml", "feature", "docx", "html"]
_TEXT_TYPES = {"text/plain": ".txt", "text/markdown": ".md", "text/csv": ".csv", "application/json": ".json",
               "application/yaml": ".yaml", "application/x-yaml": ".yaml", "text/yaml": ".yaml"}
_BINARY_TYPES = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp"}
_LOGIN_HINTS = ("login", "signin", "sign-in", "sign_in", "accounts.google.com", "auth", "sso")

URL_RE = re.compile(r"https?://[^\s<>\"'|]+")
FIGMA_RE = re.compile(r"^https?://(?:www\.)?figma\.com/(?:file|design|proto|board)/([A-Za-z0-9]+)")
GDOC_RE = re.compile(r"^https?://docs\.google\.com/document/d/([A-Za-z0-9_-]+)")
CONF_PAGE_RE = re.compile(r"/wiki/spaces/[^/]+/pages/(\d+)")
CONF_TINY_RE = re.compile(r"/wiki/x/([A-Za-z0-9_-]+)")


@dataclass
class Credentials:
    """Tokens the bot may use to read linked sources. Never passed to the agent."""
    figma_token: str | None = None
    confluence_email: str | None = None
    confluence_token: str | None = None
    # Hostnames the Confluence credentials may be sent to; empty = any *.atlassian.net site.
    confluence_sites: set[str] = field(default_factory=set)

    @classmethod
    def from_env(cls) -> "Credentials":
        sites = {h.strip().lower() for h in os.environ.get("CONFLUENCE_SITES", "").split(",") if h.strip()}
        return cls(
            figma_token=os.environ.get("FIGMA_TOKEN") or None,
            confluence_email=os.environ.get("CONFLUENCE_EMAIL") or None,
            confluence_token=os.environ.get("CONFLUENCE_API_TOKEN") or None,
            confluence_sites=sites,
        )

    @property
    def confluence_enabled(self) -> bool:
        return bool(self.confluence_email and self.confluence_token)

    def confluence_allowed(self, host: str) -> bool:
        host = host.lower()
        return host in self.confluence_sites if self.confluence_sites else host.endswith(".atlassian.net")


@dataclass
class Source:
    kind: str  # "upload" | "link"
    label: str  # file name or URL as the user gave it
    path: Path | None = None  # saved file (None when it couldn't be read)
    note: str = ""  # why it failed, or what was extracted

    @property
    def ok(self) -> bool:
        return self.path is not None


class FetchError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def parse_links(text: str) -> list[str]:
    """Extract http(s) URLs (any separator), strip trailing punctuation, de-duplicate, keep order."""
    seen, links = set(), []
    for m in URL_RE.finditer(text or ""):
        url = m.group(0).rstrip(".,;:)]}>")
        if url not in seen:
            seen.add(url)
            links.append(url)
    return links


def safe_name(name: str, default: str = "file") -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", name or "").strip("-.")[:80]
    return stem or default


def _unique(dest_dir: Path, name: str) -> Path:
    path = dest_dir / name
    stem, suffix, n = path.stem, path.suffix, 2
    while path.exists():
        path = dest_dir / f"{stem}-{n}{suffix}"
        n += 1
    return path


def is_public_host(host: str) -> bool:
    """Block SSRF: refuse hosts that resolve to loopback, private, link-local or reserved addresses."""
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            return False
    return True


class _PublicOnlyRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not is_public_host(urllib.parse.urlparse(newurl).hostname or ""):
            raise FetchError("redirected to a non-public address")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_get(url: str, headers: dict | None = None, check_public: bool = True) -> tuple[str, str, bytes]:
    """GET with redirect + size limits. Returns (final_url, content_type, body). Raises FetchError."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError("only http(s) links are supported")
    if check_public and not is_public_host(parsed.hostname or ""):
        raise FetchError("host is not reachable from the public internet")
    opener = urllib.request.build_opener(_PublicOnlyRedirects())
    req = urllib.request.Request(url, headers={"User-Agent": "TestCaseGeneratorBot/1.0", **(headers or {})})
    try:
        with opener.open(req, timeout=HTTP_TIMEOUT) as resp:
            body = resp.read(MAX_DOWNLOAD_BYTES + 1)
            if len(body) > MAX_DOWNLOAD_BYTES:
                raise FetchError(f"larger than {MAX_DOWNLOAD_BYTES // (1024 * 1024)} MB")
            ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return resp.geturl(), ctype, body
    except urllib.error.HTTPError as exc:
        detail = _error_detail(exc)
        if exc.code in (401, 403):
            raise FetchError("needs sign-in (access denied)" + (f": {detail}" if detail else "")) from exc
        raise FetchError(f"HTTP {exc.code}" + (f": {detail}" if detail else "")) from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"could not connect ({exc.reason})") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise FetchError("timed out") from exc


def _error_detail(exc: urllib.error.HTTPError) -> str:
    """Short reason from a JSON error body (Figma 'err', Atlassian 'message'), if any."""
    try:
        data = json.loads(exc.read(4096) or b"{}")
    except (ValueError, OSError):
        return ""
    if not isinstance(data, dict):
        return ""
    msg = data.get("err") or data.get("message") or ""
    if not msg and isinstance(data.get("errors"), list) and data["errors"]:
        msg = (data["errors"][0] or {}).get("title", "")
    return str(msg)[:200]


class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head", "template"}
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "pre", "table"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.title = ""
        self._skip = 0
        self._in_title = False
        self._cell = 0  # inside <td>/<th>: keep the cell on one line so rows stay readable

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in self.SKIP:
            self._skip += 1
        elif tag in ("td", "th"):
            self._cell += 1
            self.parts.append("| ")
        elif tag in self.BLOCK:
            self.parts.append(" " if self._cell else "\n")
        if tag in ("h1", "h2", "h3") and not self._cell:
            self.parts.append("#" * int(tag[1]) + " ")
        if tag == "li" and not self._cell:
            self.parts.append("- ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in ("td", "th"):
            self._cell = max(0, self._cell - 1)
            self.parts.append(" ")
        elif tag == "tr":
            self.parts.append("|\n")
        elif tag in self.BLOCK:
            self.parts.append(" " if self._cell else "\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self._skip:
            self.parts.append(data)


def html_to_text(html: str) -> tuple[str, str]:
    """(title, readable text) from an HTML page."""
    parser = _TextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\|\s*\n\s*\|", "|\n|", text)
    text = re.sub(r"\n\s*\n\s*(\n\s*)+", "\n\n", text)
    return parser.title.strip(), "\n".join(line.strip() for line in text.splitlines()).strip()


def _looks_like_login(final_url: str) -> bool:
    parsed = urllib.parse.urlparse(final_url)
    hay = (parsed.hostname or "") + parsed.path.lower()
    return any(h in hay for h in _LOGIN_HINTS)


# ---------------------------------------------------------------- links

def _save_text(dest_dir: Path, base: str, url: str, text: str, title: str = "") -> Path:
    path = _unique(dest_dir, f"{safe_name(base, 'page')}.md")
    header = f"<!-- Source: {url} -->\n" + (f"# {title}\n\n" if title else "")
    path.write_text(header + text + "\n", encoding="utf-8")
    return path


def fetch_generic(url: str, dest_dir: Path) -> Source:
    try:
        final_url, ctype, body = http_get(url)
    except FetchError as exc:
        return Source("link", url, note=str(exc))
    if _looks_like_login(final_url):
        return Source("link", url, note="needs sign-in; upload the document as a file instead")

    base = Path(urllib.parse.urlparse(final_url).path).stem or urllib.parse.urlparse(final_url).hostname or "page"
    if ctype in _BINARY_TYPES:
        path = _unique(dest_dir, safe_name(base) + _BINARY_TYPES[ctype])
        path.write_bytes(body)
        return Source("link", url, path)
    if ctype in _TEXT_TYPES or ctype.startswith("text/") and ctype != "text/html":
        path = _unique(dest_dir, safe_name(base) + _TEXT_TYPES.get(ctype, ".txt"))
        path.write_bytes(body)
        return Source("link", url, path)
    if ctype in ("text/html", "application/xhtml+xml", ""):
        title, text = html_to_text(body.decode("utf-8", errors="replace"))
        if len(text) < MIN_PAGE_TEXT:
            return Source("link", url, note="page has no readable text (probably needs sign-in or JavaScript); upload an export instead")
        return Source("link", url, _save_text(dest_dir, title or base, url, text, title))
    return Source("link", url, note=f"unsupported content type {ctype}")


def fetch_google_doc(url: str, doc_id: str, dest_dir: Path) -> Source:
    export = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        final_url, ctype, body = http_get(export)
    except FetchError:
        return Source("link", url, note="Google Doc isn't shared as 'Anyone with the link'; share it that way or upload a PDF export")
    if _looks_like_login(final_url) or ctype == "text/html":
        return Source("link", url, note="Google Doc isn't shared as 'Anyone with the link'; share it that way or upload a PDF export")
    text = body.decode("utf-8-sig", errors="replace")
    return Source("link", url, _save_text(dest_dir, f"google-doc-{doc_id[:12]}", url, text))


def parse_figma(url: str) -> tuple[str, str | None] | None:
    """(file_key, api node id or None) for a Figma URL; node-id '12-34' / '12%3A34' -> '12:34'."""
    m = FIGMA_RE.match(url)
    if not m:
        return None
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    node = (query.get("node-id") or [None])[0]
    return m.group(1), node.replace("-", ":") if node else None


def _figma_json(path: str, token: str) -> dict:
    _, _, body = http_get(f"https://api.figma.com{path}", headers={"X-Figma-Token": token})
    return json.loads(body)


def _pick_frames(children: list[dict]) -> tuple[list[dict], list[dict]]:
    """Visible screens on a page (loose components only if there's nothing else) -> (exported, skipped)."""
    top = [n for n in children if n.get("visible", True)]
    frames = [n for n in top if n.get("type") in ("FRAME", "SECTION")] or \
             [n for n in top if n.get("type") in ("COMPONENT", "COMPONENT_SET")]
    return frames[:MAX_FIGMA_FRAMES], frames[MAX_FIGMA_FRAMES:]


def fetch_figma(url: str, dest_dir: Path, token: str | None) -> list[Source]:
    key, node = parse_figma(url)
    skipped: list[dict] = []
    if not token:
        return [Source("link", url, note="Figma links need FIGMA_TOKEN on the bot; or upload a PNG export of the frames")]
    try:
        names: dict[str, str] = {}
        if node:
            # A link copied from the canvas usually points at the whole page (e.g. node-id=0-1): expand it to its
            # screens, otherwise every screen is squeezed into one unreadable image.
            data = _figma_json(f"/v1/files/{key}/nodes?ids={urllib.parse.quote(node)}&depth=1", token)
            linked = ((data.get("nodes") or {}).get(node) or {}).get("document") or {}
            if linked.get("type") == "CANVAS":
                frames, skipped = _pick_frames(linked.get("children", []))
                if not frames:
                    return [Source("link", url, note="the linked Figma page has no screens (frames)")]
                ids = [f["id"] for f in frames]
                names = {f["id"]: f.get("name", "") for f in frames}
            else:
                ids = [node]
                names = {node: linked.get("name", "")}
        else:
            doc = _figma_json(f"/v1/files/{key}?depth=2", token)
            pages = doc.get("document", {}).get("children", [])
            frames, skipped = _pick_frames(pages[0].get("children", []) if pages else [])
            ids = [f["id"] for f in frames]
            names = {f["id"]: f.get("name", "") for f in frames}
            if not ids:
                return [Source("link", url, note="no top-level frames on the first page; link a specific frame (node-id)")]
        images = _figma_json(f"/v1/images/{key}?ids={urllib.parse.quote(','.join(ids))}&format=png&scale=2", token)
        if images.get("err"):
            return [Source("link", url, note=f"Figma error: {images['err']}")]
    except FetchError as exc:
        reason = str(exc)
        if "file_content:read" in reason or "scope" in reason.lower():
            msg = "FIGMA_TOKEN lacks the 'File content: Read-only' scope; generate a new token with it"
        elif "sign-in" in reason:
            msg = "Figma token can't access this file (is it shared with the token's Figma account?)"
        else:
            msg = f"Figma API: {reason}"
        return [Source("link", url, note=msg)]

    sources = []
    if skipped:
        sources.append(Source("link", f"{url} ({len(skipped)} more frames: {', '.join(f.get('name', '') for f in skipped)[:150]})",
                              note=f"skipped: only the first {MAX_FIGMA_FRAMES} frames are exported; link other frames directly"))
    for node_id, image_url in images.get("images", {}).items():
        label = f"{url} (frame {names.get(node_id) or node_id})"
        if not image_url:
            sources.append(Source("link", label, note="frame could not be rendered (hidden or empty)"))
            continue
        try:
            _, _, png = http_get(image_url)
        except FetchError as exc:
            sources.append(Source("link", label, note=str(exc)))
            continue
        path = _unique(dest_dir, f"figma-{safe_name(names.get(node_id) or node_id.replace(':', '-'))}.png")
        path.write_bytes(png)
        sources.append(Source("link", label, path))
    return sources


def is_confluence_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return (parsed.hostname or "").lower().endswith(".atlassian.net") and parsed.path.startswith("/wiki")


def decode_tiny_link(code: str) -> int:
    """Confluence /wiki/x/<code>: URL-safe base64 of the page id as little-endian bytes, trailing zero bytes trimmed."""
    std = code.replace("-", "/").replace("_", "+")
    raw = base64.b64decode(std + "A" * (-len(std) % 4))
    return int.from_bytes(raw, "little")


def _page_id_from_url(url: str) -> int | None:
    parsed = urllib.parse.urlparse(url)
    m = CONF_PAGE_RE.search(parsed.path)
    if m:
        return int(m.group(1))
    page_id = (urllib.parse.parse_qs(parsed.query).get("pageId") or [None])[0]
    return int(page_id) if page_id and page_id.isdigit() else None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # surface the 30x as an HTTPError so the Location header can be read


def resolve_confluence_page_id(url: str, auth_header: str) -> int | None:
    """Page id from a page URL, a ?pageId= URL, or a /wiki/x/ short link (redirect first, decoding as fallback)."""
    page_id = _page_id_from_url(url)
    if page_id:
        return page_id
    m = CONF_TINY_RE.search(urllib.parse.urlparse(url).path)
    if not m:
        return None
    opener = urllib.request.build_opener(_NoRedirect())
    req = urllib.request.Request(url, headers={"Authorization": auth_header, "User-Agent": "TestCaseGeneratorBot/1.0"})
    try:
        with opener.open(req, timeout=HTTP_TIMEOUT):
            pass
    except urllib.error.HTTPError as exc:
        location = exc.headers.get("Location") or ""
        resolved = _page_id_from_url(urllib.parse.urljoin(url, location))
        if resolved:
            return resolved
    except (urllib.error.URLError, TimeoutError, socket.timeout):
        pass
    try:
        return decode_tiny_link(m.group(1))
    except (ValueError, base64.binascii.Error):
        return None


@functools.lru_cache(maxsize=16)
def _cloud_id(host: str) -> str:
    """Site's cloud id (public endpoint), needed to route scoped API tokens through api.atlassian.com."""
    _, _, info = http_get(f"https://{host}/_edge/tenant_info")
    return json.loads(info)["cloudId"]


def _confluence_get(path: str, host: str, auth_header: str) -> dict:
    """GET a v2 API path on the site; if the token is rejected, retry through the api.atlassian.com gateway (scoped tokens)."""
    headers = {"Authorization": auth_header, "Accept": "application/json"}
    try:
        _, _, body = http_get(f"https://{host}{path}", headers=headers)
        return json.loads(body)
    except FetchError as exc:
        if "sign-in" not in str(exc) and "HTTP 401" not in str(exc):
            raise
    _, _, body = http_get(f"https://api.atlassian.com/ex/confluence/{_cloud_id(host)}{path}", headers=headers)
    return json.loads(body)


MAX_CONFLUENCE_CHILDREN = 5


def _page_error(exc: FetchError, page_id: int) -> str:
    reason = str(exc)
    if "sign-in" in reason or "HTTP 401" in reason:
        return "Confluence rejected the credentials (check CONFLUENCE_EMAIL / CONFLUENCE_API_TOKEN and the token's read scopes)"
    if "HTTP 404" in reason:
        return f"page {page_id} not found, or the account behind the token can't view it"
    return reason


def _fetch_page(page_id: int, label: str, host: str, auth_header: str, dest_dir: Path) -> Source:
    try:
        page = _confluence_get(f"/wiki/api/v2/pages/{page_id}?body-format=view", host, auth_header)
    except FetchError as exc:
        return Source("link", label, note=_page_error(exc, page_id))
    except (KeyError, ValueError) as exc:
        return Source("link", label, note=f"unexpected Confluence response ({exc})")

    title = page.get("title") or f"Page {page_id}"
    html = ((page.get("body") or {}).get("view") or {}).get("value") or ""
    _, text = html_to_text(html)
    if not text.strip():
        return Source("link", label, note=f"Confluence page '{title}' has no text content")
    version = (page.get("version") or {}).get("number")
    meta = f"Confluence page {page_id}" + (f", version {version}" if version else "")
    path = _unique(dest_dir, f"confluence-{page_id}-{safe_name(title, 'page')[:50]}.md")
    path.write_text(f"<!-- Source: {label} ({meta}) -->\n# {title}\n\n{text}\n", encoding="utf-8")
    return Source("link", label, path, note=f"Confluence: {title}")


def _child_pages(page_id: int, host: str, auth_header: str) -> list[dict]:
    try:
        data = _confluence_get(f"/wiki/api/v2/pages/{page_id}/direct-children?limit=25", host, auth_header)
    except (FetchError, KeyError, ValueError):
        return []
    return [c for c in data.get("results", []) if c.get("type", "page") == "page" and c.get("status", "current") == "current"]


def fetch_confluence(url: str, dest_dir: Path, creds: Credentials) -> list[Source]:
    """The linked page plus its direct child pages (hub pages usually keep the PRD/RFC one level down)."""
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    if not creds.confluence_enabled:
        return [Source("link", url, note="Confluence links need CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN on the bot; "
                                         "or paste the page text into Feature context / upload a PDF export")]
    if not creds.confluence_allowed(host):
        return [Source("link", url, note=f"{host} is not in CONFLUENCE_SITES, so the bot won't send credentials there")]
    token = base64.b64encode(f"{creds.confluence_email}:{creds.confluence_token}".encode()).decode()
    auth_header = f"Basic {token}"

    page_id = resolve_confluence_page_id(url, auth_header)
    if not page_id:
        return [Source("link", url, note="not a Confluence page link (use the page URL or its short link)")]
    main = _fetch_page(page_id, url, host, auth_header, dest_dir)
    if not main.ok:
        return [main]

    sources = [main]
    children = _child_pages(page_id, host, auth_header)
    for child in children[:MAX_CONFLUENCE_CHILDREN]:
        label = f"{url} › {child.get('title') or child['id']}"
        sources.append(_fetch_page(int(child["id"]), label, host, auth_header, dest_dir))
    if len(children) > MAX_CONFLUENCE_CHILDREN:
        sources.append(Source("link", f"{url} › {len(children) - MAX_CONFLUENCE_CHILDREN} more child pages",
                              note=f"skipped: only the first {MAX_CONFLUENCE_CHILDREN} child pages are read; link the others directly"))
    return sources


def fetch_link(url: str, dest_dir: Path, creds: Credentials | None = None) -> list[Source]:
    creds = creds or Credentials()
    if is_confluence_url(url):
        return fetch_confluence(url, dest_dir, creds)
    if parse_figma(url):
        return fetch_figma(url, dest_dir, creds.figma_token)
    gdoc = GDOC_RE.match(url)
    if gdoc:
        return [fetch_google_doc(url, gdoc.group(1), dest_dir)]
    return [fetch_generic(url, dest_dir)]


# ---------------------------------------------------------------- Slack uploads

def docx_to_text(path: Path) -> Path | None:
    """macOS textutil conversion; None when unavailable."""
    if not shutil.which("textutil"):
        return None
    out = path.with_suffix(".txt")
    result = subprocess.run(["textutil", "-convert", "txt", "-output", str(out), str(path)], capture_output=True, timeout=60)
    return out if result.returncode == 0 and out.exists() else None


def save_upload(file_info: dict, bot_token: str, dest_dir: Path) -> Source:
    """Download one Slack file (full file object from files.info) into dest_dir."""
    name = file_info.get("name") or file_info.get("title") or file_info.get("id", "upload")
    ext = (file_info.get("filetype") or Path(name).suffix.lstrip(".")).lower()
    if ext not in UPLOAD_FILETYPES:
        return Source("upload", name, note=f"file type '{ext}' isn't supported")
    if (file_info.get("size") or 0) > MAX_DOWNLOAD_BYTES:
        return Source("upload", name, note=f"larger than {MAX_DOWNLOAD_BYTES // (1024 * 1024)} MB")
    url = file_info.get("url_private_download") or file_info.get("url_private")
    if not url:
        return Source("upload", name, note="Slack returned no download URL")
    try:
        _, ctype, body = http_get(url, headers={"Authorization": f"Bearer {bot_token}"})
    except FetchError as exc:
        return Source("upload", name, note=f"download failed: {exc}")
    if ctype == "text/html" and ext != "html":
        return Source("upload", name, note="download failed: the bot needs the files:read scope")
    filename = safe_name(Path(name).stem) + "." + ("jpg" if ext == "jpeg" else ext)
    path = _unique(dest_dir, filename)
    path.write_bytes(body)
    if ext == "docx":
        converted = docx_to_text(path)
        if not converted:
            return Source("upload", name, note="couldn't convert DOCX to text on this machine; upload a PDF instead")
        return Source("upload", name, converted)
    if ext == "html":
        title, text = html_to_text(body.decode("utf-8", errors="replace"))
        path.unlink()
        return Source("upload", name, _save_text(dest_dir, Path(name).stem, name, text, title))
    return Source("upload", name, path)


def collect_sources(links: list[str], uploads: list[dict], dest_dir: Path,
                    bot_token: str = "", creds: Credentials | None = None) -> list[Source]:
    """Fetch every link and upload; failures are returned as Sources with a note, never raised."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    sources: list[Source] = []
    for info in uploads:
        try:
            sources.append(save_upload(info, bot_token, dest_dir))
        except Exception as exc:  # one bad file must not sink the run
            sources.append(Source("upload", info.get("name", "upload"), note=f"failed: {exc}"))
    for url in links[:MAX_LINKS]:
        try:
            sources.extend(fetch_link(url, dest_dir, creds))
        except Exception as exc:
            sources.append(Source("link", url, note=f"failed: {exc}"))
    for url in links[MAX_LINKS:]:
        sources.append(Source("link", url, note=f"skipped: only the first {MAX_LINKS} links are read"))
    return sources
