"""Transparent behavioral review rules for safely emulated malware-like traffic."""

from __future__ import annotations

import hashlib
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import timedelta
from pathlib import PureWindowsPath
from typing import Any, Iterable

from .telemetry import TelemetryEvent


@dataclass(frozen=True)
class BehaviorFinding:
    finding_id: str
    rule_id: str
    title: str
    severity: str
    mitre_technique: str
    host: str
    process: str
    evidence_ids: tuple[str, ...]
    evidence: str
    recommendation: str
    asset_context: dict[str, Any]
    classification: str = "behavior-review"
    confirmed_malware: bool = False
    confirmed_vulnerability: bool = False
    automatic_response_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence_ids"] = list(self.evidence_ids)
        return result


@dataclass(frozen=True)
class DetectorThresholds:
    """Explicit rule thresholds; defaults reproduce the frozen V1.0 detector."""

    beh_001_minimum_connections: int = 6
    beh_001_minimum_mean_interval_seconds: float = 5
    beh_001_maximum_mean_interval_seconds: float = 900
    beh_001_maximum_interval_cv: float = 0.15
    beh_002_minimum_distinct_endpoints: int = 8
    beh_002_interval_seconds: int = 60
    beh_003_minimum_bytes_sent: int = 1_000_000
    beh_003_minimum_sent_received_ratio: float = 10
    beh_004_minimum_bytes_received: int = 32_768
    beh_004_maximum_delay_seconds: int = 120

    def __post_init__(self) -> None:
        if self.beh_001_minimum_connections < 2:
            raise ValueError("BEH-001 minimum connections must be at least 2")
        if not 0 < self.beh_001_minimum_mean_interval_seconds <= self.beh_001_maximum_mean_interval_seconds:
            raise ValueError("BEH-001 mean-interval bounds are invalid")
        if self.beh_001_maximum_interval_cv < 0:
            raise ValueError("BEH-001 maximum interval CV cannot be negative")
        if self.beh_002_minimum_distinct_endpoints < 2 or self.beh_002_interval_seconds < 1:
            raise ValueError("BEH-002 thresholds are invalid")
        if self.beh_003_minimum_bytes_sent < 1 or self.beh_003_minimum_sent_received_ratio <= 0:
            raise ValueError("BEH-003 thresholds are invalid")
        if self.beh_004_minimum_bytes_received < 1 or self.beh_004_maximum_delay_seconds < 0:
            raise ValueError("BEH-004 thresholds are invalid")


def inventory_context(hosts: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index Nmap inventory without turning fingerprints into vulnerability claims."""
    context: dict[str, dict[str, Any]] = {}
    for host in hosts:
        services = [
            {
                "port": item.get("port", ""),
                "protocol": item.get("protocol", ""),
                "service": item.get("service", ""),
                "product": item.get("product", ""),
                "version": item.get("version", ""),
            }
            for item in host.get("ports", [])
        ]
        item = {
            "known_asset": True,
            "hostname": host.get("hostname", ""),
            "operating_system_guess": host.get("os", "Unknown"),
            "observed_services": services,
        }
        if host.get("ip"):
            context[str(host["ip"])] = item
        if host.get("hostname"):
            context[str(host["hostname"])] = item
    return context


class BehaviorDetector:
    """Flag reviewable behavior while preserving evidence and uncertainty."""

    RULE_IDS = {"BEH-001", "BEH-002", "BEH-003", "BEH-004"}

    def __init__(
        self,
        inventory: dict[str, dict[str, Any]] | None = None,
        thresholds: DetectorThresholds | None = None,
    ):
        self.inventory = inventory or {}
        self.thresholds = thresholds or DetectorThresholds()

    def analyze(self, events: list[TelemetryEvent]) -> list[BehaviorFinding]:
        findings = [
            *self._periodic_beaconing(events),
            *self._rapid_service_discovery(events),
            *self._asymmetric_egress(events),
            *self._download_then_file_create(events),
        ]
        return sorted(findings, key=lambda item: (item.rule_id, item.host, item.finding_id))

    def _asset_context(self, host: str) -> dict[str, Any]:
        return self.inventory.get(host, {"known_asset": False, "observed_services": []})

    @staticmethod
    def _finding_id(rule_id: str, evidence: list[TelemetryEvent]) -> str:
        material = "|".join(item.event_id for item in evidence).encode("utf-8")
        return f"{rule_id}-{hashlib.sha256(material).hexdigest()[:12]}"

    def _periodic_beaconing(self, events: list[TelemetryEvent]) -> list[BehaviorFinding]:
        groups: dict[tuple[str, str, str, int | None], list[TelemetryEvent]] = defaultdict(list)
        for event in events:
            if event.event_type != "network_connection":
                continue
            destination = event.destination_domain or event.destination_ip
            groups[(event.host, event.process, destination, event.destination_port)].append(event)

        findings = []
        for (host, process, destination, port), group in groups.items():
            ordered = sorted(group, key=lambda item: item.timestamp)
            if len(ordered) < self.thresholds.beh_001_minimum_connections:
                continue
            intervals = [
                (current.timestamp - previous.timestamp).total_seconds()
                for previous, current in zip(ordered, ordered[1:])
            ]
            mean_interval = statistics.fmean(intervals)
            if not (
                self.thresholds.beh_001_minimum_mean_interval_seconds
                <= mean_interval
                <= self.thresholds.beh_001_maximum_mean_interval_seconds
            ):
                continue
            variation = statistics.pstdev(intervals) / mean_interval if mean_interval else float("inf")
            if variation > self.thresholds.beh_001_maximum_interval_cv:
                continue
            evidence = ordered[:20]
            findings.append(
                BehaviorFinding(
                    finding_id=self._finding_id("BEH-001", evidence),
                    rule_id="BEH-001",
                    title="Periodic outbound communication requires review",
                    severity="medium",
                    mitre_technique="T1071",
                    host=host,
                    process=process,
                    evidence_ids=tuple(item.event_id for item in evidence),
                    evidence=(
                        f"{len(ordered)} connections to {destination}:{port} had a mean interval of "
                        f"{mean_interval:.1f}s and coefficient of variation {variation:.3f}."
                    ),
                    recommendation=(
                        "Validate the process owner and destination, compare with an approved update schedule, "
                        "and collect proxy or DNS evidence before considering a temporary egress restriction."
                    ),
                    asset_context=self._asset_context(host),
                )
            )
        return findings

    def _rapid_service_discovery(self, events: list[TelemetryEvent]) -> list[BehaviorFinding]:
        groups: dict[tuple[str, str], list[TelemetryEvent]] = defaultdict(list)
        for event in events:
            if event.event_type == "network_connection":
                groups[(event.host, event.process)].append(event)

        findings = []
        window = timedelta(seconds=self.thresholds.beh_002_interval_seconds)
        for (host, process), group in groups.items():
            ordered = sorted(group, key=lambda item: item.timestamp)
            matched: list[TelemetryEvent] = []
            endpoint_counts: dict[tuple[str, int | None], int] = defaultdict(int)
            right = 0
            for left, first in enumerate(ordered):
                while right < len(ordered) and ordered[right].timestamp - first.timestamp <= window:
                    endpoint = (
                        ordered[right].destination_ip or ordered[right].destination_domain,
                        ordered[right].destination_port,
                    )
                    endpoint_counts[endpoint] += 1
                    right += 1
                if len(endpoint_counts) >= self.thresholds.beh_002_minimum_distinct_endpoints:
                    matched = ordered[left : min(right, left + 20)]
                    break
                endpoint = (first.destination_ip or first.destination_domain, first.destination_port)
                endpoint_counts[endpoint] -= 1
                if endpoint_counts[endpoint] == 0:
                    del endpoint_counts[endpoint]
            if not matched:
                continue
            findings.append(
                BehaviorFinding(
                    finding_id=self._finding_id("BEH-002", matched),
                    rule_id="BEH-002",
                    title="Rapid network-service discovery requires review",
                    severity="high",
                    mitre_technique="T1046",
                    host=host,
                    process=process,
                    evidence_ids=tuple(item.event_id for item in matched),
                    evidence=(
                        "The process contacted at least "
                        f"{self.thresholds.beh_002_minimum_distinct_endpoints} distinct network endpoints within "
                        f"{self.thresholds.beh_002_interval_seconds} seconds."
                    ),
                    recommendation=(
                        "Confirm whether the process is an authorized scanner, inspect its execution context, "
                        "and use segmentation or rate controls only after validating business impact."
                    ),
                    asset_context=self._asset_context(host),
                )
            )
        return findings

    def _asymmetric_egress(self, events: list[TelemetryEvent]) -> list[BehaviorFinding]:
        findings = []
        for event in events:
            if (
                event.event_type != "network_connection"
                or event.bytes_sent < self.thresholds.beh_003_minimum_bytes_sent
            ):
                continue
            ratio = event.bytes_sent / max(event.bytes_received, 1)
            if ratio < self.thresholds.beh_003_minimum_sent_received_ratio:
                continue
            findings.append(
                BehaviorFinding(
                    finding_id=self._finding_id("BEH-003", [event]),
                    rule_id="BEH-003",
                    title="High-volume asymmetric egress requires review",
                    severity="high",
                    mitre_technique="T1041",
                    host=event.host,
                    process=event.process,
                    evidence_ids=(event.event_id,),
                    evidence=(
                        f"One connection sent {event.bytes_sent} bytes and received {event.bytes_received} "
                        f"bytes (ratio {ratio:.1f}:1)."
                    ),
                    recommendation=(
                        "Validate the transfer's business purpose and destination, preserve flow evidence, "
                        "and consider egress restriction or host isolation only after confirmation."
                    ),
                    asset_context=self._asset_context(event.host),
                )
            )
        return findings

    def _download_then_file_create(self, events: list[TelemetryEvent]) -> list[BehaviorFinding]:
        network_events = [item for item in events if item.event_type == "network_connection"]
        executable_like_suffixes = {".bin", ".dll", ".exe", ".msi", ".ps1", ".zip"}
        findings = []
        for file_event in (item for item in events if item.event_type == "file_create"):
            if PureWindowsPath(file_event.path).suffix.lower() not in executable_like_suffixes:
                continue
            candidates = [
                item
                for item in network_events
                if item.host == file_event.host
                and item.process == file_event.process
                and 0
                <= (file_event.timestamp - item.timestamp).total_seconds()
                <= self.thresholds.beh_004_maximum_delay_seconds
                and item.bytes_received >= self.thresholds.beh_004_minimum_bytes_received
            ]
            if not candidates:
                continue
            connection = max(candidates, key=lambda item: item.timestamp)
            evidence = [connection, file_event]
            findings.append(
                BehaviorFinding(
                    finding_id=self._finding_id("BEH-004", evidence),
                    rule_id="BEH-004",
                    title="Network download followed by file creation requires review",
                    severity="high",
                    mitre_technique="T1105",
                    host=file_event.host,
                    process=file_event.process,
                    evidence_ids=tuple(item.event_id for item in evidence),
                    evidence=(
                        f"The process received {connection.bytes_received} bytes and created "
                        f"{PureWindowsPath(file_event.path).name!r} within 120 seconds."
                    ),
                    recommendation=(
                        "Preserve the file hash and process lineage, validate the download source, and quarantine "
                        "the file or restrict the destination only through an approved incident-response action."
                    ),
                    asset_context=self._asset_context(file_event.host),
                )
            )
        return findings
