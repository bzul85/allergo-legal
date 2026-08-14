#!/usr/bin/env python3
"""Convert the published legal HTML into the plain-text asset bundled in the app.

The app must show exactly the text that is published on the website, and it must
work offline, so the text is shipped inside the APK rather than fetched. This
script is the one-off converter used whenever the documents change; it is not
part of the Flutter build.

Usage:
    python3 tools/build_app_asset.py <path-to-AllerGo-repo>
"""

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VERSION = "2026-08-14"

BASE_URL = "https://bzul85.github.io/allergo-legal"

SOURCES = {
    "terms": {"pl": "pl/terms/index.html", "en": "terms/index.html"},
    "privacy": {"pl": "pl/privacy/index.html", "en": "privacy/index.html"},
}

URLS = {
    "terms": {"pl": f"{BASE_URL}/pl/terms/", "en": f"{BASE_URL}/terms/"},
    "privacy": {"pl": f"{BASE_URL}/pl/privacy/", "en": f"{BASE_URL}/privacy/"},
}

BLOCK_TAGS = {"p", "h1", "h2", "h3", "li", "div"}


class LegalTextParser(HTMLParser):
    """Flattens the document body into readable plain text.

    Ordered lists keep their numbering because the documents refer to specific
    paragraphs ("the recommendations in paragraph 3"), so the numbers carry
    meaning and cannot be dropped.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.title = None
        self._in_h1 = False
        self._skip_depth = 0
        self.blocks = []
        self._buffer = []
        self._list_stack = []
        self._prefix = ""

    # -- helpers ---------------------------------------------------------

    def _flush(self, blank_after=False):
        text = "".join(self._buffer)
        # Collapsing whitespace would eat the list indentation, so the marker is
        # kept aside and prepended once the text itself is normalised.
        text = re.sub(r"\s+", " ", text).strip()
        prefix = self._prefix
        self._buffer = []
        self._prefix = ""
        if text:
            self.blocks.append(prefix + text)
            if blank_after:
                self.blocks.append("")

    # -- parser callbacks ------------------------------------------------

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "main":
            self.in_main = True
            return
        if tag == "h1":
            self._in_h1 = True
            return
        if not self.in_main or self._skip_depth:
            return

        if tag in ("script", "style"):
            self._skip_depth += 1
            return
        if tag in ("ol", "ul"):
            self._flush()
            self._list_stack.append([tag, 0])
            return
        if tag == "li":
            self._flush()
            if self._list_stack:
                frame = self._list_stack[-1]
                frame[1] += 1
                depth = len(self._list_stack) - 1
                indent = "    " * depth
                marker = f"{frame[1]}." if frame[0] == "ol" else "•"
                self._prefix = f"{indent}{marker} "
            return
        if tag in ("h2", "h3"):
            self._flush(blank_after=True)
            return
        if tag == "p":
            self._flush()
            return
        if tag == "br":
            self._buffer.append(" ")

    def handle_endtag(self, tag):
        if tag == "main":
            self._flush()
            self.in_main = False
            return
        if tag == "h1":
            self._in_h1 = False
            return
        if not self.in_main:
            return
        if tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag in ("ol", "ul"):
            self._flush()
            if self._list_stack:
                self._list_stack.pop()
            if not self._list_stack:
                self.blocks.append("")
            return
        if tag in BLOCK_TAGS:
            self._flush(blank_after=tag in ("p", "h2", "h3"))

    def handle_data(self, data):
        if self._in_h1 and self.title is None:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self.title = cleaned
        if self.in_main and not self._skip_depth:
            self._buffer.append(data)

    # -- result ----------------------------------------------------------

    def text(self):
        lines = []
        for block in self.blocks:
            if block == "" and (not lines or lines[-1] == ""):
                continue
            lines.append(block)
        while lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines)


def convert(path: Path):
    parser = LegalTextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    body = parser.text()
    if not body:
        raise SystemExit(f"No <main> content extracted from {path}")
    return html.unescape(parser.title or ""), body


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    app_repo = Path(sys.argv[1]).expanduser()
    legal_repo = Path(__file__).resolve().parent.parent

    documents = {}
    for doc, languages in SOURCES.items():
        documents[doc] = {}
        for language, relative in languages.items():
            title, body = convert(legal_repo / relative)
            documents[doc][language] = {"title": title, "body": body}
            print(f"{doc:8} {language}  {len(body):6d} chars  {title}")

    payload = {
        "version": VERSION,
        "urls": URLS,
        "documents": documents,
    }

    target = app_repo / "assets" / "legal" / "legal.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
