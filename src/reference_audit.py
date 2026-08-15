"""Resolve BibTeX DOI metadata through Crossref and preserve an auditable report."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

ENTRY_PATTERN = re.compile(r"^@(?P<type>\w+)\{(?P<key>[^,]+),(?P<body>.*?)(?=^@|\Z)", re.MULTILINE | re.DOTALL)
FIELD_PATTERN = re.compile(r"^\s*(?P<name>\w+)\s*=\s*\{(?P<value>.*)\},?\s*$", re.MULTILINE)


def parse_bibliography(text: str) -> list[dict[str, Any]]:
    entries = []
    for match in ENTRY_PATTERN.finditer(text):
        fields = {
            field.group("name").lower(): field.group("value").strip()
            for field in FIELD_PATTERN.finditer(match.group("body"))
        }
        entries.append({"key": match.group("key").strip(), "type": match.group("type").lower(), **fields})
    return entries


def _crossref_year(message: dict[str, Any]) -> int | None:
    for field in ("published-print", "published-online", "published", "issued", "created"):
        parts = message.get(field, {}).get("date-parts", [])
        if parts and parts[0] and isinstance(parts[0][0], int):
            return parts[0][0]
    return None


def _datacite_year(attributes: dict[str, Any]) -> int | None:
    year = attributes.get("publicationYear")
    return int(year) if isinstance(year, (int, str)) and str(year).isdigit() else None


def audit_dois(bibliography: str | Path, output: str | Path) -> dict[str, Any]:
    source = Path(bibliography).resolve()
    entries = parse_bibliography(source.read_text(encoding="utf-8"))
    records = []
    session = requests.Session()
    session.headers["User-Agent"] = (
        "network-security-review-reference-audit/1.1 (https://github.com/awakyy1/network-security-review)"
    )
    for entry in entries:
        doi = entry.get("doi")
        if not doi:
            records.append(
                {
                    "key": entry["key"],
                    "citation_type": entry["type"],
                    "status": "no-doi-manual-source-check-required",
                    "url": entry.get("url"),
                }
            )
            continue
        record: dict[str, Any] = {
            "key": entry["key"],
            "citation_type": entry["type"],
            "declared_doi": doi,
            "declared_title": entry.get("title"),
            "declared_year": int(entry["year"]) if entry.get("year", "").isdigit() else entry.get("year"),
        }
        try:
            response = session.get(f"https://api.crossref.org/works/{quote(doi, safe='')}", timeout=30)
            if response.status_code == 404:
                response = session.get(f"https://api.datacite.org/dois/{quote(doi, safe='')}", timeout=30)
                response.raise_for_status()
                attributes = response.json()["data"]["attributes"]
                resolved_doi = str(attributes.get("doi", ""))
                resolved_year = _datacite_year(attributes)
                record.update(
                    {
                        "status": "resolved",
                        "metadata_provider": "DataCite",
                        "doi_matches": resolved_doi.lower() == doi.lower(),
                        "resolved_doi": resolved_doi,
                        "resolved_title": (attributes.get("titles") or [{}])[0].get("title"),
                        "resolved_authors": [
                            " ".join(part for part in (author.get("given", ""), author.get("family", "")) if part)
                            for author in attributes.get("creators", [])
                        ],
                        "resolved_year": resolved_year,
                        "year_matches": resolved_year == record["declared_year"],
                        "publisher": attributes.get("publisher"),
                        "resource_type": attributes.get("types", {}).get("resourceTypeGeneral"),
                        "resource_url": attributes.get("url"),
                    }
                )
            else:
                response.raise_for_status()
                message = response.json()["message"]
                resolved_doi = str(message.get("DOI", ""))
                resolved_year = _crossref_year(message)
                record.update(
                    {
                        "status": "resolved",
                        "metadata_provider": "Crossref",
                        "doi_matches": resolved_doi.lower() == doi.lower(),
                        "resolved_doi": resolved_doi,
                        "resolved_title": (message.get("title") or [None])[0],
                        "resolved_authors": [
                            " ".join(part for part in (author.get("given", ""), author.get("family", "")) if part)
                            for author in message.get("author", [])
                        ],
                        "resolved_year": resolved_year,
                        "year_matches": resolved_year == record["declared_year"],
                        "container_title": (message.get("container-title") or [None])[0],
                        "publisher": message.get("publisher"),
                        "resource_type": message.get("type"),
                        "resource_url": message.get("resource", {}).get("primary", {}).get("URL"),
                    }
                )
        except (requests.RequestException, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            record.update({"status": "resolution-error", "error_type": type(error).__name__, "error": str(error)})
        records.append(record)
    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bibliography": source.name,
        "entries": len(entries),
        "doi_entries": sum("doi" in item for item in entries),
        "resolved_dois": sum(item.get("status") == "resolved" for item in records),
        "metadata_mismatches": [
            item["key"]
            for item in records
            if item.get("status") == "resolved" and not (item.get("doi_matches") and item.get("year_matches"))
        ],
        "scope_note": (
            "Resolution verifies identifier and basic metadata only. Source-to-claim support, peer-review status, "
            "venue quality, and retraction/correction status require separate human checks against primary sources."
        ),
        "records": records,
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bibliography", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        result = audit_dois(arguments.bibliography, arguments.output)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print(
        f"Reference audit: entries={result['entries']} doi={result['doi_entries']} "
        f"resolved={result['resolved_dois']} mismatches={len(result['metadata_mismatches'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
