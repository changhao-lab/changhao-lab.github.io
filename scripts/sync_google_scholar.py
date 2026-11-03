#!/usr/bin/env python3
"""Add newly listed Google Scholar works to the lab website.

The script is intentionally append-only: it never deletes or rewrites the
bibliographic content of an existing publication. If Scholar cannot be read,
the script exits with an error before touching the data file.
"""

import argparse
import html
import json
import re
import sys
import time
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

import yaml


SCHOLAR_ID = "2YZzmdUAAAAJ"
PROFILE_URL = (
    "https://scholar.google.com/citations"
    f"?hl=en&user={SCHOLAR_ID}&view_op=list_works&sortby=pubdate&pagesize=100"
)
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0 Safari/537.36 "
    "ChangHaoLab-Publication-Sync/1.0"
)
DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def clean_text(value):
    return " ".join(html.unescape(value).split())


def normalize_title(value):
    normalized = unicodedata.normalize("NFKD", clean_text(value)).casefold()
    return "".join(character for character in normalized if character.isalnum())


def normalize_doi(value):
    value = unquote(clean_text(value)).strip()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I)
    match = DOI_PATTERN.search(value)
    if not match:
        return ""
    return match.group(0).rstrip(".,;:)]}\"'").casefold()


class CaptureParser(HTMLParser):
    """Small HTML capture helper that does not require a scraping dependency."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.capture_kind = None
        self.capture_depth = 0
        self.capture_parts = []

    def start_capture(self, kind):
        self.capture_kind = kind
        self.capture_depth = 1
        self.capture_parts = []

    def handle_data(self, data):
        if self.capture_kind:
            self.capture_parts.append(data)

    def capture_starttag(self, tag):
        if not self.capture_kind:
            return False
        if tag not in VOID_TAGS:
            self.capture_depth += 1
        return True

    def capture_endtag(self, tag):
        if not self.capture_kind:
            return False
        if tag not in VOID_TAGS:
            self.capture_depth -= 1
        if self.capture_depth == 0:
            kind = self.capture_kind
            value = clean_text("".join(self.capture_parts))
            self.capture_kind = None
            self.capture_parts = []
            self.capture_complete(kind, value)
        return True

    def capture_complete(self, kind, value):
        raise NotImplementedError


class ScholarListParser(CaptureParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if self.capture_starttag(tag):
            return

        attributes = {key: value or "" for key, value in attrs}
        classes = set(attributes.get("class", "").split())

        if tag == "tr" and "gsc_a_tr" in classes:
            self.current = {"title": "", "detail_url": "", "gray": [], "year": ""}
            return

        if self.current is None:
            return

        if tag == "a" and "gsc_a_at" in classes:
            self.current["detail_url"] = urljoin("https://scholar.google.com", attributes.get("href", ""))
            self.start_capture("title")
        elif tag == "div" and "gs_gray" in classes:
            self.start_capture("gray")
        elif tag == "span" and ("gsc_a_h" in classes or "gsc_a_y" in classes):
            self.start_capture("year")

    def handle_endtag(self, tag):
        if self.capture_endtag(tag):
            return
        if tag == "tr" and self.current is not None:
            if self.current["title"]:
                self.rows.append(self.current)
            self.current = None

    def capture_complete(self, kind, value):
        if self.current is None:
            return
        if kind == "gray":
            self.current["gray"].append(value)
        elif value:
            self.current[kind] = value


class ScholarDetailParser(CaptureParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.fields = {}
        self.last_field = ""
        self.title = ""
        self.title_url = ""
        self.hrefs = []
        self.meta = {}
        self.all_text = []

    def handle_starttag(self, tag, attrs):
        if self.capture_starttag(tag):
            return

        attributes = {key: value or "" for key, value in attrs}
        classes = set(attributes.get("class", "").split())

        if tag == "a" and attributes.get("href"):
            href = urljoin(self.base_url, attributes["href"])
            self.hrefs.append(href)
            if "gsc_oci_title_link" in classes:
                self.title_url = href
                self.start_capture("title")
                return

        if tag == "div" and "gsc_oci_field" in classes:
            self.start_capture("field")
        elif tag == "div" and "gsc_oci_value" in classes:
            self.start_capture("value")
        elif tag == "meta":
            name = attributes.get("name", "").casefold()
            content = clean_text(attributes.get("content", ""))
            if name and content:
                self.meta.setdefault(name, []).append(content)

    def handle_endtag(self, tag):
        self.capture_endtag(tag)

    def handle_data(self, data):
        self.all_text.append(data)
        super().handle_data(data)

    def capture_complete(self, kind, value):
        if kind == "field":
            self.last_field = value
        elif kind == "value" and self.last_field:
            self.fields[self.last_field.casefold()] = value
            self.last_field = ""
        elif kind == "title":
            self.title = value


def fetch_html(url, attempts=3):
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    last_error = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
                return body.decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Could not read Google Scholar after {attempts} attempts: {last_error}")


def parse_profile(document):
    parser = ScholarListParser()
    parser.feed(document)
    if not parser.rows:
        lower_document = document.casefold()
        if "unusual traffic" in lower_document or "not a robot" in lower_document:
            raise RuntimeError("Google Scholar returned an anti-bot page instead of the public profile")
        raise RuntimeError("No publications were found in the Google Scholar profile response")
    return parser.rows


def first_meta(parser, name):
    values = parser.meta.get(name, [])
    return values[0] if values else ""


def find_doi(parser):
    candidates = [
        parser.fields.get("doi", ""),
        first_meta(parser, "citation_doi"),
        parser.title_url,
        *parser.hrefs,
        " ".join(parser.all_text),
    ]
    for candidate in candidates:
        doi = normalize_doi(candidate)
        if doi:
            return doi
    return ""


def extract_year(*values):
    for value in values:
        match = YEAR_PATTERN.search(value or "")
        if match:
            return int(match.group(0))
    return None


def scholar_id_from_url(url):
    values = parse_qs(urlparse(url).query).get("citation_for_view", [])
    return values[0] if values else ""


def publication_from_row(row):
    detail_url = row["detail_url"]
    detail_document = fetch_html(detail_url)
    detail = ScholarDetailParser(detail_url)
    detail.feed(detail_document)

    gray = row.get("gray", [])
    authors = detail.fields.get("authors", "") or first_meta(detail, "citation_author")
    if not authors and gray:
        authors = gray[0]

    publication_date = detail.fields.get("publication date", "")
    year = extract_year(row.get("year", ""), publication_date, first_meta(detail, "citation_date"))
    if year is None:
        raise RuntimeError(f"No publication year was found for {row['title']!r}")

    journal = ""
    for field_name in ("journal", "conference", "book", "publication", "publisher"):
        if detail.fields.get(field_name):
            journal = detail.fields[field_name]
            break
    journal = journal or first_meta(detail, "citation_journal_title")
    if not journal and len(gray) > 1:
        journal = re.sub(r",?\s*(?:19|20)\d{2}\s*$", "", gray[1]).strip(" ,")
    journal = journal or "Publication"

    doi = find_doi(detail)
    publisher_url = detail.title_url
    if publisher_url.startswith("https://scholar.google.") or not publisher_url:
        publisher_url = f"https://doi.org/{doi}" if doi else detail_url

    return {
        "year": year,
        "authors": clean_text(authors) or "Hao Chang",
        "title": clean_text(detail.title) or clean_text(row["title"]),
        "url": publisher_url,
        "journal": clean_text(journal),
        "doi": doi,
        "scholar_id": scholar_id_from_url(detail_url),
    }


def load_publications(path):
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    data = yaml.safe_load(raw.decode("utf-8")) or {}

    if isinstance(data.get("items"), list):
        items = data["items"]
    elif isinstance(data.get("years"), list):
        items = []
        for group in data["years"]:
            for item in group.get("items", []):
                items.append({"year": group["year"], **item})
    else:
        raise RuntimeError(f"{path} does not contain an items list")

    if not all(isinstance(item, dict) and item.get("title") for item in items):
        raise RuntimeError(f"{path} contains an invalid publication entry")
    return items, newline


def render_publications(items, newline):
    lines = ["items:"]
    for item in items:
        lines.append(f"  - year: {int(item['year'])}")
        for field in ("authors", "title", "url", "journal", "doi", "scholar_id"):
            if field == "scholar_id" and not item.get(field):
                continue
            value = str(item.get(field, ""))
            lines.append(f"    {field}: {json.dumps(value, ensure_ascii=False)}")
    return (newline.join(lines) + newline).encode("utf-8")


def add_new_publications(existing, profile_rows):
    known_titles = {normalize_title(str(item.get("title", ""))) for item in existing}
    known_dois = {normalize_doi(str(item.get("doi", ""))) for item in existing}
    known_dois.discard("")
    known_ids = {str(item.get("scholar_id", "")) for item in existing}
    known_ids.discard("")

    candidates = []
    for row in profile_rows:
        row_id = scholar_id_from_url(row.get("detail_url", ""))
        if normalize_title(row["title"]) in known_titles or (row_id and row_id in known_ids):
            continue
        candidates.append(row)

    if len(candidates) > 50:
        raise RuntimeError(
            f"Scholar returned {len(candidates)} unknown works; refusing an unusually large automatic update"
        )

    added = []
    for row in candidates:
        publication = publication_from_row(row)
        title_key = normalize_title(publication["title"])
        doi_key = normalize_doi(publication["doi"])
        scholar_id = publication.get("scholar_id", "")
        if title_key in known_titles or (doi_key and doi_key in known_dois):
            continue
        if scholar_id and scholar_id in known_ids:
            continue
        added.append(publication)
        known_titles.add(title_key)
        if doi_key:
            known_dois.add(doi_key)
        if scholar_id:
            known_ids.add(scholar_id)

    combined = added + existing
    combined = [item for _, item in sorted(enumerate(combined), key=lambda pair: (-int(pair[1]["year"]), pair[0]))]
    return combined, added


def parse_args():
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-url", default=PROFILE_URL)
    parser.add_argument(
        "--data-file",
        type=Path,
        default=repository_root / "_data" / "publications.yml",
    )
    parser.add_argument("--profile-html", type=Path, help="Read a saved profile page instead of the network")
    parser.add_argument("--dry-run", action="store_true", help="Report additions without writing the YAML file")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        existing, newline = load_publications(args.data_file)
        if args.profile_html:
            profile_document = args.profile_html.read_text(encoding="utf-8")
        else:
            profile_document = fetch_html(args.profile_url)
        rows = parse_profile(profile_document)
        combined, added = add_new_publications(existing, rows)
    except Exception as error:
        print(f"Publication sync failed: {error}", file=sys.stderr)
        return 1

    if not added:
        print(f"No new publications found. Scholar returned {len(rows)} works.")
        return 0

    for publication in added:
        print(f"Adding {publication['year']}: {publication['title']}")

    if args.dry_run:
        print(f"Dry run complete; {len(added)} publication(s) would be added.")
        return 0

    args.data_file.write_bytes(render_publications(combined, newline))
    print(f"Added {len(added)} publication(s) to {args.data_file}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
