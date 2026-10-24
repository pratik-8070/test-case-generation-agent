"""Reference-material fetching (links, Figma, Google Docs, Slack uploads) with the network mocked."""

import io
import json
import shutil
import urllib.error
import urllib.parse
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers  # noqa: F401  (puts the project root on sys.path)

from slack_bot import sources as S

PAGE = "<html><head><title>Cart PRD</title><script>var x=1</script></head><body><h1>Cart</h1>" + \
       "<p>Shoppers can add up to 10 units of a product. " * 10 + "</p><ul><li>AC1: toast shown</li></ul></body></html>"


class HelperTests(unittest.TestCase):
    def test_parse_links(self):
        text = "PRD (https://a.example/prd), RFC: https://b.example/rfc.\nhttps://a.example/prd\nnot a link"
        self.assertEqual(S.parse_links(text), ["https://a.example/prd", "https://b.example/rfc"])

    def test_private_hosts_blocked(self):
        for host in ("127.0.0.1", "10.0.0.5", "192.168.1.1", "169.254.169.254", "localhost", "::1", ""):
            self.assertFalse(S.is_public_host(host), host)
        self.assertTrue(S.is_public_host("8.8.8.8"))

    def test_http_get_refuses_private_and_non_http(self):
        with self.assertRaises(S.FetchError):
            S.http_get("http://127.0.0.1:8080/admin")
        with self.assertRaises(S.FetchError):
            S.http_get("file:///etc/passwd")

    def test_html_to_text(self):
        title, text = S.html_to_text(PAGE)
        self.assertEqual(title, "Cart PRD")
        self.assertIn("# Cart", text)
        self.assertIn("- AC1: toast shown", text)
        self.assertNotIn("var x", text)

    def test_parse_figma(self):
        self.assertEqual(S.parse_figma("https://www.figma.com/design/AbC123/Shop?node-id=12-34&t=x"), ("AbC123", "12:34"))
        self.assertEqual(S.parse_figma("https://figma.com/file/AbC123/Shop"), ("AbC123", None))
        self.assertEqual(S.parse_figma("https://www.figma.com/proto/K9/x?node-id=1%3A2"), ("K9", "1:2"))
        self.assertIsNone(S.parse_figma("https://example.com/design/AbC123"))


class FetchTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_public_html_page_saved_as_markdown(self):
        with mock.patch.object(S, "http_get", return_value=("https://a.example/prd", "text/html", PAGE.encode())):
            [src] = S.fetch_link("https://a.example/prd", self.dir)
        self.assertTrue(src.ok)
        content = src.path.read_text()
        self.assertTrue(content.startswith("<!-- Source: https://a.example/prd -->"))
        self.assertIn("up to 10 units", content)

    def test_login_redirect_and_empty_spa_are_reported(self):
        with mock.patch.object(S, "http_get", return_value=("https://id.example.com/login?next=x", "text/html", PAGE.encode())):
            [src] = S.fetch_link("https://wiki.example.com/prd", self.dir)
        self.assertFalse(src.ok)
        self.assertIn("sign-in", src.note)
        with mock.patch.object(S, "http_get", return_value=("https://app.example.com/doc", "text/html", b"<div id=root></div>")):
            [src] = S.fetch_link("https://app.example.com/doc", self.dir)
        self.assertIn("no readable text", src.note)

    def test_pdf_link_kept_as_pdf(self):
        with mock.patch.object(S, "http_get", return_value=("https://a.example/rfc-42.pdf", "application/pdf", b"%PDF-1.7")):
            [src] = S.fetch_link("https://a.example/rfc-42.pdf", self.dir)
        self.assertEqual(src.path.name, "rfc-42.pdf")

    def test_google_doc(self):
        url = "https://docs.google.com/document/d/1AbCdEf_ghIJ/edit"
        with mock.patch.object(S, "http_get", return_value=("https://docs.google.com/x", "text/plain", "PRD text".encode())) as get:
            [src] = S.fetch_link(url, self.dir)
        self.assertEqual(get.call_args[0][0], "https://docs.google.com/document/d/1AbCdEf_ghIJ/export?format=txt")
        self.assertIn("PRD text", src.path.read_text())
        with mock.patch.object(S, "http_get", return_value=("https://accounts.google.com/signin", "text/html", b"")):
            [src] = S.fetch_link(url, self.dir)
        self.assertIn("Anyone with the link", src.note)

    def test_figma_without_token(self):
        [src] = S.fetch_link("https://www.figma.com/design/AbC123/Shop?node-id=1-2", self.dir, creds=S.Credentials())
        self.assertIn("FIGMA_TOKEN", src.note)

    def test_figma_whole_file_exports_top_level_frames(self):
        doc = {"document": {"children": [{"type": "CANVAS", "children": [
            {"id": "1:2", "name": "Cart page", "type": "FRAME"},
            {"id": "1:3", "name": "Hidden", "type": "FRAME", "visible": False},
            {"id": "1:4", "name": "Checkout", "type": "SECTION"},
            {"id": "1:6", "name": "Button/Primary", "type": "COMPONENT"},
            {"id": "1:5", "name": "note", "type": "TEXT"}]}]}}
        images = {"err": None, "images": {"1:2": "https://s3.example/a.png", "1:4": None}}

        def fake_get(url, headers=None, check_public=True):
            if "/v1/files/" in url:
                self.assertEqual(headers, {"X-Figma-Token": "tok"})
                return url, "application/json", json.dumps(doc).encode()
            if "/v1/images/" in url:
                self.assertIn("ids=1%3A2%2C1%3A4", url)
                return url, "application/json", json.dumps(images).encode()
            return url, "image/png", b"\x89PNG"

        with mock.patch.object(S, "http_get", side_effect=fake_get):
            got = S.fetch_link("https://www.figma.com/design/AbC123/Shop", self.dir, creds=S.Credentials(figma_token="tok"))
        self.assertEqual([s.ok for s in got], [True, False])
        self.assertEqual(got[0].path.name, "figma-Cart-page.png")
        self.assertIn("could not be rendered", got[1].note)

    def test_http_error_detail_is_kept(self):
        err = urllib.error.HTTPError("u", 403, "Forbidden", {}, io.BytesIO(b'{"status":403,"err":"Invalid scope(s): current_user:read"}'))
        opener = mock.Mock()
        opener.open.side_effect = err
        with mock.patch.object(S.urllib.request, "build_opener", return_value=opener), \
                mock.patch.object(S, "is_public_host", return_value=True):
            with self.assertRaises(S.FetchError) as ctx:
                S.http_get("https://api.figma.com/v1/files/K")
        self.assertIn("Invalid scope(s): current_user:read", str(ctx.exception))

    def test_figma_missing_scope(self):
        with mock.patch.object(S, "http_get", side_effect=S.FetchError(
                "needs sign-in (access denied): Invalid scope(s): current_user:read. This endpoint requires the file_content:read scope")):
            [src] = S.fetch_link("https://www.figma.com/design/AbC123/Shop", self.dir, creds=S.Credentials(figma_token="tok"))
        self.assertIn("lacks the 'File content: Read-only' scope", src.note)

    def test_figma_page_link_expands_to_screens(self):
        page = {"nodes": {"0:1": {"document": {"type": "CANVAS", "name": "Flow", "children": [
            {"id": "1:1", "name": "Button/Primary", "type": "COMPONENT"},
            {"id": "2:1", "name": "01 Choose type", "type": "FRAME"},
            {"id": "2:2", "name": "02 Details", "type": "FRAME"}]}}}}

        def fake_get(url, headers=None, check_public=True):
            if "/nodes?ids=0%3A1&depth=1" in url:
                return url, "application/json", json.dumps(page).encode()
            if "/v1/images/" in url:
                self.assertIn("ids=2%3A1%2C2%3A2", url)  # screens, not the page or the component
                return url, "application/json", json.dumps({"images": {"2:1": "https://s3/a.png", "2:2": "https://s3/b.png"}}).encode()
            return url, "image/png", b"\x89PNG"

        with mock.patch.object(S, "http_get", side_effect=fake_get):
            got = S.fetch_link("https://www.figma.com/design/K1/Flow?node-id=0-1&p=f", self.dir, creds=S.Credentials(figma_token="tok"))
        self.assertEqual([s.path.name for s in got], ["figma-01-Choose-type.png", "figma-02-Details.png"])

    def test_figma_single_frame_link_uses_its_name(self):
        def fake_get(url, headers=None, check_public=True):
            if "/nodes?" in url:
                return url, "application/json", json.dumps({"nodes": {"2:1": {"document": {"type": "FRAME", "name": "01 Choose type"}}}}).encode()
            if "/v1/images/" in url:
                return url, "application/json", json.dumps({"images": {"2:1": "https://s3/a.png"}}).encode()
            return url, "image/png", b"\x89PNG"

        with mock.patch.object(S, "http_get", side_effect=fake_get):
            [src] = S.fetch_link("https://www.figma.com/design/K1/Flow?node-id=2-1", self.dir, creds=S.Credentials(figma_token="tok"))
        self.assertEqual(src.path.name, "figma-01-Choose-type.png")

    def test_figma_frame_limit_reports_skipped(self):
        frames = [{"id": f"1:{i}", "name": f"Screen {i}", "type": "FRAME"} for i in range(14)]
        doc = {"document": {"children": [{"type": "CANVAS", "children": frames}]}}

        def fake_get(url, headers=None, check_public=True):
            if "/v1/files/" in url:
                return url, "application/json", json.dumps(doc).encode()
            if "/v1/images/" in url:
                ids = urllib.parse.unquote(url.split("ids=")[1].split("&")[0]).split(",")
                return url, "application/json", json.dumps({"images": {i: "https://s3.example/x.png" for i in ids}}).encode()
            return url, "image/png", b"\x89PNG"

        with mock.patch.object(S, "http_get", side_effect=fake_get):
            got = S.fetch_link("https://www.figma.com/design/K1/Flow", self.dir, creds=S.Credentials(figma_token="tok"))
        self.assertEqual(sum(s.ok for s in got), 12)
        skipped = [s for s in got if not s.ok]
        self.assertEqual(len(skipped), 1)
        self.assertTrue(skipped[0].note.startswith("skipped:"))
        self.assertIn("Screen 12, Screen 13", skipped[0].label)

    def test_figma_access_denied(self):
        with mock.patch.object(S, "http_get", side_effect=S.FetchError("needs sign-in (access denied)")):
            [src] = S.fetch_link("https://www.figma.com/design/AbC123/Shop?node-id=1-2", self.dir, creds=S.Credentials(figma_token="tok"))
        self.assertIn("can't access this file", src.note)

    def test_upload_download_and_type_checks(self):
        info = {"id": "F1", "name": "Cart RFC.pdf", "filetype": "pdf", "size": 100, "url_private_download": "https://files.slack.com/x"}
        with mock.patch.object(S, "http_get", return_value=("https://files.slack.com/x", "application/pdf", b"%PDF")) as get:
            src = S.save_upload(info, "xoxb-test", self.dir)
        self.assertEqual(get.call_args.kwargs["headers"], {"Authorization": "Bearer xoxb-test"})
        self.assertEqual(src.path.name, "Cart-RFC.pdf")
        self.assertIn("isn't supported", S.save_upload({"name": "a.exe", "filetype": "exe"}, "t", self.dir).note)
        self.assertIn("larger than", S.save_upload({"name": "a.pdf", "filetype": "pdf", "size": 10**9}, "t", self.dir).note)
        with mock.patch.object(S, "http_get", return_value=("https://slack.com/signin", "text/html", b"<html>")):
            self.assertIn("files:read", S.save_upload(info, "t", self.dir).note)

    def test_collect_sources_never_raises_and_caps_links(self):
        links = [f"https://a.example/{i}" for i in range(12)]
        with mock.patch.object(S, "fetch_link", side_effect=RuntimeError("boom")):
            got = S.collect_sources(links, [], self.dir)
        self.assertEqual(len(got), 12)
        self.assertTrue(all(not s.ok for s in got))
        self.assertIn("only the first 10", got[-1].note)


CONF = S.Credentials(confluence_email="me@example.com", confluence_token="tok", confluence_sites={"acme.atlassian.net"})
PAGE_JSON = {"id": "720897", "title": "Checkout PRD", "version": {"number": 7},
             "body": {"view": {"representation": "view", "value": "<h2>Acceptance criteria</h2><ul><li>AC1: Coupon applies before shipping</li></ul>"}}}


class ConfluenceTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_url_helpers(self):
        self.assertEqual(S.decode_tiny_link("AQAL"), 720897)
        self.assertEqual(S.decode_tiny_link("AQAB"), 65537)
        self.assertEqual(S._page_id_from_url("https://acme.atlassian.net/wiki/spaces/ENG/pages/123456/Checkout+PRD"), 123456)
        self.assertEqual(S._page_id_from_url("https://acme.atlassian.net/wiki/pages/viewpage.action?pageId=98765"), 98765)
        self.assertTrue(S.is_confluence_url("https://acme.atlassian.net/wiki/x/AQAL"))
        self.assertFalse(S.is_confluence_url("https://acme.atlassian.net/jira/browse/X-1"))

    def test_credentials_and_site_allow_list(self):
        [src] = S.fetch_link("https://acme.atlassian.net/wiki/x/AQAL", self.dir, S.Credentials())
        self.assertIn("CONFLUENCE_EMAIL", src.note)
        [src] = S.fetch_link("https://evil.atlassian.net/wiki/x/AQAL", self.dir, CONF)
        self.assertIn("not in CONFLUENCE_SITES", src.note)
        open_creds = S.Credentials(confluence_email="e", confluence_token="t")
        self.assertTrue(open_creds.confluence_allowed("anything.atlassian.net"))
        self.assertFalse(open_creds.confluence_allowed("atlassian.net.evil.com"))

    def test_tiny_link_resolved_by_redirect(self):
        err = urllib.error.HTTPError("u", 302, "Found", {"Location": "/wiki/spaces/ENG/pages/555/Checkout"}, io.BytesIO())
        opener = mock.Mock()
        opener.open.side_effect = err
        with mock.patch.object(S.urllib.request, "build_opener", return_value=opener):
            self.assertEqual(S.resolve_confluence_page_id("https://acme.atlassian.net/wiki/x/AQAL", "Basic x"), 555)
        opener.open.side_effect = urllib.error.HTTPError("u", 302, "Found", {"Location": "/login?dest-url=x"}, io.BytesIO())
        with mock.patch.object(S.urllib.request, "build_opener", return_value=opener):
            self.assertEqual(S.resolve_confluence_page_id("https://acme.atlassian.net/wiki/x/AQAL", "Basic x"), 720897)

    def test_page_fetched_as_markdown(self):
        with mock.patch.object(S, "resolve_confluence_page_id", return_value=720897), \
                mock.patch.object(S, "http_get", return_value=("u", "application/json", json.dumps(PAGE_JSON).encode())) as get:
            [src] = S.fetch_link("https://acme.atlassian.net/wiki/x/AQAL", self.dir, CONF)
        first = get.call_args_list[0]
        self.assertEqual(first.args[0], "https://acme.atlassian.net/wiki/api/v2/pages/720897?body-format=view")
        self.assertTrue(first.kwargs["headers"]["Authorization"].startswith("Basic "))
        self.assertTrue(src.ok)
        self.assertEqual(src.path.name, "confluence-720897-Checkout-PRD.md")
        content = src.path.read_text()
        self.assertIn("# Checkout PRD", content)
        self.assertIn("- AC1: Coupon applies before shipping", content)
        self.assertIn("version 7", content)

    def test_scoped_token_falls_back_to_gateway(self):
        S._cloud_id.cache_clear()
        calls = []

        def fake_get(url, headers=None, check_public=True):
            calls.append(url)
            if url.startswith("https://acme.atlassian.net/wiki/api"):
                raise S.FetchError("needs sign-in (access denied)")
            if url.endswith("/_edge/tenant_info"):
                return url, "application/json", b'{"cloudId": "c-1"}'
            return url, "application/json", json.dumps(PAGE_JSON).encode()

        with mock.patch.object(S, "resolve_confluence_page_id", return_value=720897), mock.patch.object(S, "http_get", side_effect=fake_get):
            [src] = S.fetch_link("https://acme.atlassian.net/wiki/x/AQAL", self.dir, CONF)
        self.assertTrue(src.ok)
        self.assertIn("https://api.atlassian.com/ex/confluence/c-1/wiki/api/v2/pages/720897?body-format=view", calls)
        self.assertEqual(sum(u.endswith("/_edge/tenant_info") for u in calls), 1)  # cloud id cached

    def test_hub_page_reads_direct_children(self):
        children = {"results": [{"id": "101", "title": "PRD", "type": "page", "status": "current"},
                                {"id": "102", "title": "Whiteboard", "type": "whiteboard", "status": "current"},
                                {"id": "103", "title": "RFC", "type": "page", "status": "current"}]}

        def fake_get(path, host, auth):
            if path.endswith("/direct-children?limit=25"):
                return children
            pid = path.split("/pages/")[1].split("?")[0]
            title = {"720897": "Hub", "101": "PRD", "103": "RFC"}[pid]
            return {"title": title, "body": {"view": {"value": f"<p>{title} body FR-1</p>"}}}

        with mock.patch.object(S, "resolve_confluence_page_id", return_value=720897), \
                mock.patch.object(S, "_confluence_get", side_effect=fake_get):
            got = S.fetch_link("https://acme.atlassian.net/wiki/x/AQAL", self.dir, CONF)
        self.assertEqual([s.path.name for s in got], ["confluence-720897-Hub.md", "confluence-101-PRD.md", "confluence-103-RFC.md"])
        self.assertTrue(got[1].label.endswith("› PRD"))

    def test_tables_keep_rows_together(self):
        html = ("<table><tr><th><p>Type</p></th><th><p>Pricing</p></th></tr>"
                "<tr><td><p>Luxury</p></td><td><p>Fixed price, min ₹50,000</p></td></tr></table><p>After</p>")
        _, text = S.html_to_text(html)
        self.assertIn("| Type | Pricing |", text)
        self.assertIn("| Luxury | Fixed price, min ₹50,000 |", text)
        self.assertIn("After", text)

    def test_errors_are_explained(self):
        cases = [(S.FetchError("needs sign-in (access denied)"), "rejected the credentials"),
                 (S.FetchError("HTTP 404"), "not found, or the account")]
        for exc, expected in cases:
            with mock.patch.object(S, "resolve_confluence_page_id", return_value=1), \
                    mock.patch.object(S, "_confluence_get", side_effect=exc):
                [src] = S.fetch_link("https://acme.atlassian.net/wiki/x/AQAB", self.dir, CONF)
            self.assertIn(expected, src.note)


if __name__ == "__main__":
    unittest.main()
