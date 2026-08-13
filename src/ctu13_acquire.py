"""Safely acquire only the frozen CTU-13 labeled text-flow files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

ALLOWED_HOST = "mcfp.felk.cvut.cz"
ALLOWED_SUFFIX = ".binetflow"
MAX_SOURCE_BYTES = 100 * 1024 * 1024
BLOCKED_SUFFIXES = {".exe", ".zip", ".pcap", ".bz2", ".biargus"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        manifest = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to load CTU-13 manifest: {error}") from error
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list):
        raise ValueError("CTU-13 manifest must contain a sources array")
    roles = {item.get("role") for item in manifest["sources"] if isinstance(item, dict)}
    if roles != {"development", "holdout"}:
        raise ValueError("CTU-13 manifest must freeze one development and one holdout source")
    return manifest


def _validate_source(source: dict[str, Any]) -> None:
    required = {"scenario", "capture", "family", "role", "filename", "url", "content_length", "etag", "sha256"}
    if not required <= set(source):
        raise ValueError("Every CTU-13 source must contain the frozen provenance fields")
    filename = source["filename"]
    if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(ALLOWED_SUFFIX):
        raise ValueError("CTU-13 acquisition permits only a basename ending in .binetflow")
    parsed = urlparse(source["url"])
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST or not parsed.path.endswith(f"/{filename}"):
        raise ValueError("CTU-13 source must be an approved HTTPS .binetflow URL on the official host")
    if any(parsed.path.lower().endswith(suffix) for suffix in BLOCKED_SUFFIXES):
        raise ValueError("Executable, archive, packet-capture and binary Argus files are prohibited")
    length = source["content_length"]
    if isinstance(length, bool) or not isinstance(length, int) or not 1 <= length <= MAX_SOURCE_BYTES:
        raise ValueError("CTU-13 source content length is outside the approved bound")
    digest = source["sha256"]
    if digest is not None and (not isinstance(digest, str) or len(digest) != 64):
        raise ValueError("CTU-13 source SHA-256 must be null or a 64-character digest")


def acquire_sources(
    manifest_path: str | Path,
    data_directory: str | Path,
    *,
    download: bool,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Verify frozen sources and optionally download their text flow files."""
    manifest = load_manifest(manifest_path)
    data_root = Path(data_directory).resolve()
    data_root.mkdir(parents=True, exist_ok=True)
    client = session or requests.Session()
    records = []

    for source in manifest["sources"]:
        if not isinstance(source, dict):
            raise ValueError("Every CTU-13 source must be an object")
        _validate_source(source)
        target = (data_root / source["filename"]).resolve()
        if target.parent != data_root:
            raise ValueError("CTU-13 target escaped the selected data directory")

        if not target.is_file() and not download:
            raise ValueError(f"Missing CTU-13 source: {target}; rerun with --download")
        if not target.is_file():
            temporary = target.with_suffix(target.suffix + ".part")
            response = client.get(
                source["url"],
                headers={"User-Agent": "network-security-review-v2/1.0"},
                stream=True,
                timeout=(10, 120),
                allow_redirects=False,
            )
            response.raise_for_status()
            if int(response.headers.get("Content-Length", -1)) != source["content_length"]:
                raise ValueError(f"Unexpected CTU-13 content length for {source['filename']}")
            if response.headers.get("ETag") != source["etag"]:
                raise ValueError(f"Unexpected CTU-13 ETag for {source['filename']}")
            with temporary.open("wb") as stream:
                for block in response.iter_content(chunk_size=1024 * 1024):
                    if block:
                        stream.write(block)
            if temporary.stat().st_size != source["content_length"]:
                temporary.unlink(missing_ok=True)
                raise ValueError(f"Incomplete CTU-13 download for {source['filename']}")
            temporary.replace(target)

        actual_size = target.stat().st_size
        if actual_size != source["content_length"]:
            raise ValueError(f"CTU-13 file size mismatch for {source['filename']}")
        actual_digest = sha256_file(target)
        if source["sha256"] is not None and actual_digest.lower() != source["sha256"].lower():
            raise ValueError(f"CTU-13 SHA-256 mismatch for {source['filename']}")
        records.append(
            {
                "scenario": source["scenario"],
                "role": source["role"],
                "filename": source["filename"],
                "bytes": actual_size,
                "sha256": actual_digest,
                "verified_against_frozen_hash": source["sha256"] is not None,
            }
        )
    return records


def main(argv: list[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=repository_root / "research" / "v2" / "ctu13_manifest.json")
    parser.add_argument("--data-dir", type=Path, default=repository_root / "data" / "ctu13")
    parser.add_argument("--download", action="store_true", help="Download only the frozen labeled .binetflow files")
    arguments = parser.parse_args(argv)
    try:
        records = acquire_sources(arguments.manifest, arguments.data_dir, download=arguments.download)
    except (OSError, ValueError, requests.RequestException) as error:
        parser.error(str(error))
    print(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
