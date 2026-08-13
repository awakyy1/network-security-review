from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.ctu13_acquire import acquire_sources


def _manifest(payload: bytes, *, url: str | None = None) -> dict[str, object]:
    source = {
        "scenario": 5,
        "capture": "CTU-Malware-Capture-Botnet-46",
        "family": "Virut",
        "role": "development",
        "filename": "development.binetflow",
        "url": url
        or "https://mcfp.felk.cvut.cz/publicDatasets/frozen/detailed-bidirectional-flow-labels/development.binetflow",
        "content_length": len(payload),
        "etag": '"development-etag"',
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    holdout = {
        **source,
        "scenario": 12,
        "family": "NSIS.ay",
        "role": "holdout",
        "filename": "holdout.binetflow",
        "url": "https://mcfp.felk.cvut.cz/publicDatasets/frozen/detailed-bidirectional-flow-labels/holdout.binetflow",
        "etag": '"holdout-etag"',
    }
    return {"schema_version": "1.0", "sources": [source, holdout]}


class CTU13AcquireTest(unittest.TestCase):
    def test_downloads_only_frozen_text_flows_and_verifies_hashes(self) -> None:
        payload = b"StartTime,Label\n"
        response_development = Mock()
        response_development.headers = {"Content-Length": str(len(payload)), "ETag": '"development-etag"'}
        response_development.iter_content.return_value = [payload]
        response_holdout = Mock()
        response_holdout.headers = {"Content-Length": str(len(payload)), "ETag": '"holdout-etag"'}
        response_holdout.iter_content.return_value = [payload]
        session = Mock()
        session.get.side_effect = [response_development, response_holdout]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(_manifest(payload)), encoding="utf-8")

            records = acquire_sources(manifest_path, root / "data", download=True, session=session)

            self.assertEqual(len(records), 2)
            self.assertTrue(all(item["verified_against_frozen_hash"] for item in records))
            self.assertEqual((root / "data" / "development.binetflow").read_bytes(), payload)
            self.assertEqual((root / "data" / "holdout.binetflow").read_bytes(), payload)

    def test_rejects_non_official_or_dangerous_source(self) -> None:
        payload = b"safe"
        manifest = _manifest(payload, url="https://example.test/malware.exe")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "approved HTTPS .binetflow"):
                acquire_sources(manifest_path, root / "data", download=False)


if __name__ == "__main__":
    unittest.main()
