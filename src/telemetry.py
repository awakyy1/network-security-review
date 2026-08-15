"""Normalize defensive endpoint and network telemetry for the V2 research pipeline."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

ALLOWED_EVENT_TYPES = {"network_connection", "dns_query", "file_create"}
MAX_INPUT_BYTES = 20 * 1024 * 1024
MAX_EVENTS = 100_000
MAX_TEXT_LENGTH = 1_024


def _text(mapping: Mapping[str, Any], key: str, *, required: bool = False) -> str:
    value = mapping.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"Telemetry field {key!r} must be a string")
    value = value.strip()
    if required and not value:
        raise ValueError(f"Telemetry field {key!r} is required")
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"Telemetry field {key!r} exceeds {MAX_TEXT_LENGTH} characters")
    return value


def _non_negative_integer(mapping: Mapping[str, Any], key: str) -> int:
    value = mapping.get(key, 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Telemetry field {key!r} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class TelemetryEvent:
    """One normalized event; content remains observation data, not a conclusion."""

    event_id: str
    timestamp: datetime
    host: str
    event_type: str
    source: str
    process: str
    executable_path: str = ""
    signer: str = ""
    parent_process: str = ""
    user_context: str = ""
    command_line: str = ""
    file_hash_sha256: str = ""
    destination_ip: str = ""
    destination_domain: str = ""
    destination_port: int | None = None
    protocol: str = ""
    bytes_sent: int = 0
    bytes_received: int = 0
    path: str = ""

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> TelemetryEvent:
        event_type = _text(mapping, "event_type", required=True)
        if event_type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"Unsupported telemetry event type: {event_type}")

        timestamp_text = _text(mapping, "timestamp", required=True)
        try:
            timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(f"Invalid telemetry timestamp: {timestamp_text}") from error
        if timestamp.tzinfo is None:
            raise ValueError("Telemetry timestamps must include a timezone")

        destination_port = mapping.get("destination_port")
        if destination_port is not None:
            if isinstance(destination_port, bool) or not isinstance(destination_port, int):
                raise ValueError("Telemetry destination_port must be an integer")
            if not 1 <= destination_port <= 65_535:
                raise ValueError("Telemetry destination_port must be between 1 and 65535")

        event = cls(
            event_id=_text(mapping, "event_id", required=True),
            timestamp=timestamp,
            host=_text(mapping, "host", required=True),
            event_type=event_type,
            source=_text(mapping, "source", required=True),
            process=_text(mapping, "process", required=True),
            executable_path=_text(mapping, "executable_path"),
            signer=_text(mapping, "signer"),
            parent_process=_text(mapping, "parent_process"),
            user_context=_text(mapping, "user_context"),
            command_line=_text(mapping, "command_line"),
            file_hash_sha256=_text(mapping, "file_hash_sha256"),
            destination_ip=_text(mapping, "destination_ip"),
            destination_domain=_text(mapping, "destination_domain"),
            destination_port=destination_port,
            protocol=_text(mapping, "protocol"),
            bytes_sent=_non_negative_integer(mapping, "bytes_sent"),
            bytes_received=_non_negative_integer(mapping, "bytes_received"),
            path=_text(mapping, "path"),
        )
        event._validate_type_specific_fields()
        return event

    def _validate_type_specific_fields(self) -> None:
        if self.file_hash_sha256 and not re.fullmatch(r"[0-9a-fA-F]{64}", self.file_hash_sha256):
            raise ValueError("file_hash_sha256 must contain exactly 64 hexadecimal characters")
        if self.event_type == "network_connection":
            if not (self.destination_ip or self.destination_domain):
                raise ValueError("Network events require a destination_ip or destination_domain")
            if self.destination_port is None:
                raise ValueError("Network events require destination_port")
        elif self.event_type == "dns_query" and not self.destination_domain:
            raise ValueError("DNS events require destination_domain")
        elif self.event_type == "file_create" and not self.path:
            raise ValueError("File-create events require path")

    def to_evidence(self) -> dict[str, Any]:
        """Return JSON-safe evidence without adding inferred fields."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


def load_telemetry(path: str | Path) -> list[TelemetryEvent]:
    """Load bounded JSON Lines telemetry and reject duplicate evidence IDs."""
    source = Path(path)
    try:
        size = source.stat().st_size
    except OSError as error:
        raise ValueError(f"Unable to access telemetry file: {error}") from error
    if size > MAX_INPUT_BYTES:
        raise ValueError(f"Telemetry file exceeds the {MAX_INPUT_BYTES}-byte research limit")

    events: list[TelemetryEvent] = []
    identifiers: set[str] = set()
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ValueError(f"Unable to read telemetry file: {error}") from error

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        if len(events) >= MAX_EVENTS:
            raise ValueError(f"Telemetry input exceeds the {MAX_EVENTS}-event research limit")
        try:
            mapping = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON on telemetry line {line_number}: {error.msg}") from error
        if not isinstance(mapping, dict):
            raise ValueError(f"Telemetry line {line_number} must contain a JSON object")
        try:
            event = TelemetryEvent.from_mapping(mapping)
        except ValueError as error:
            raise ValueError(f"Invalid telemetry line {line_number}: {error}") from error
        if event.event_id in identifiers:
            raise ValueError(f"Duplicate telemetry event_id: {event.event_id}")
        identifiers.add(event.event_id)
        events.append(event)

    return sorted(events, key=lambda item: (item.timestamp, item.event_id))
