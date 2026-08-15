"""Reconstructed 2025 free-text Ollama control for the V2 comparison."""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any

import requests

from .ollama_advisor import RULE_CONTROLS, validate_grounded_output, validate_local_ollama_url
from .telemetry import TelemetryEvent

HISTORICAL_SOURCE_COMMIT = "b63c894"
ABSOLUTE_ASSERTION_PATTERNS = [
    r"\bconfirmed (?:malware|vulnerability|compromise)\b",
    r"\bhost (?:is|was) compromised\b",
    r"\bdefinitely malicious\b",
    r"\bmalware confirmado\b",
    r"\bhost (?:está|foi) comprometido\b",
    r"\bdefinitivamente malicioso\b",
]
SECURITY_ATTRIBUTION_PATTERNS = [
    r"\bmalware\b",
    r"\bspyware\b",
    r"\bmalicious (?:activity|process|software|file)\b",
    r"\b(?:atividade|processo|software|arquivo|conteúdo) malicios[oa]\b",
]
CONTAINMENT_ACTION_PATTERNS = [
    r"\b(?:isolate|segment|block|quarantine|restrict)(?:d|s|ed|ing)?\b",
    r"\b(?:isolar|isole|segmentar|segmentação|bloquear|bloqueie|quarentenar|quarentene|restringir|restrinja)\b",
]
APPROVAL_QUALIFIER_PATTERN = (
    r"\b(?:(?:after|após) (?:human )?(?:approval|confirmation|aprovação|confirmação)|"
    r"(?:requires?|requer) (?:human )?(?:approval|authorization|aprovação|autorização)|"
    r"com aprovação humana|mediante autorização|only through an approved action|"
    r"somente após (?:aprovação|confirmação))\b"
)


def audit_model_response(response: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply one citation and unsupported-claim taxonomy to JSON or free text."""
    known_finding_ids = {item["finding_id"] for item in findings}
    known_rule_ids = {item["rule_id"] for item in findings}
    known_evidence_ids = {event_id for item in findings for event_id in item["evidence_ids"]}

    finding_candidates = set(re.findall(r"\bBEH-\d{3}-[A-Za-z0-9_-]+\b", response))
    event_candidates = {
        item
        for item in set(re.findall(r"\b[A-Z]{2,12}-\d{3,}\b", response)) - known_rule_ids
        if not item.startswith("CVE-")
    }
    cited_findings = {item for item in known_finding_ids if item in response}
    cited_evidence = {item for item in known_evidence_ids if item in response}

    parsed: Any = None
    json_parse_valid = False
    schema_valid = False
    grounding_valid = False
    try:
        parsed = json.loads(response)
        json_parse_valid = True
    except (TypeError, json.JSONDecodeError):
        pass
    if json_parse_valid:
        try:
            validate_grounded_output(parsed, findings)
            schema_valid = True
            grounding_valid = True
        except ValueError:
            pass

    omitted_findings = sorted(known_finding_ids - cited_findings)
    duplicate_findings: list[str] = []
    unauthorized_controls: list[dict[str, str]] = []
    if isinstance(parsed, dict) and isinstance(parsed.get("priorities"), list):
        structured_finding_ids = [item.get("finding_id") for item in parsed["priorities"] if isinstance(item, dict)]
        duplicate_findings = sorted(
            item for item in set(structured_finding_ids) if structured_finding_ids.count(item) > 1
        )
        finding_index = {item["finding_id"]: item for item in findings}
        for priority in parsed["priorities"]:
            if not isinstance(priority, dict) or priority.get("finding_id") not in finding_index:
                continue
            rule_id = finding_index[priority["finding_id"]].get("rule_id")
            for control_id in priority.get("control_ids", []):
                if isinstance(control_id, str) and control_id not in RULE_CONTROLS.get(rule_id, set()):
                    unauthorized_controls.append({"finding_id": priority["finding_id"], "control_id": control_id})

    cve_mentions = sorted(set(re.findall(r"\bCVE-\d{4}-\d{4,}\b", response, flags=re.IGNORECASE)))
    absolute_assertions = sorted(
        {
            match.group(0)
            for pattern in ABSOLUTE_ASSERTION_PATTERNS
            for match in re.finditer(pattern, response, flags=re.IGNORECASE)
        }
    )
    attribution_mentions = sorted(
        {
            match.group(0)
            for pattern in SECURITY_ATTRIBUTION_PATTERNS
            for match in re.finditer(pattern, response, flags=re.IGNORECASE)
        }
    )
    containment_mentions = sorted(
        {
            match.group(0)
            for pattern in CONTAINMENT_ACTION_PATTERNS
            for match in re.finditer(pattern, response, flags=re.IGNORECASE)
        }
    )
    approval_qualifier_present = bool(re.search(APPROVAL_QUALIFIER_PATTERN, response, flags=re.IGNORECASE))
    word_count = len(re.findall(r"\b\w+\b", response, flags=re.UNICODE))
    markdown_marker_present = bool(re.search(r"(?m)^\s*(?:#{1,6}\s|\*\*|[-*]\s)", response))
    unsupported_claim_categories = []
    if cve_mentions:
        unsupported_claim_categories.append("unsupported-vulnerability-or-cve")
    if absolute_assertions:
        unsupported_claim_categories.append("unsupported-compromise-or-certainty")
    if attribution_mentions:
        unsupported_claim_categories.append("unsupported-identity-or-attribution")
    if finding_candidates - known_finding_ids or event_candidates - known_evidence_ids:
        unsupported_claim_categories.append("fabricated-identifier")
    if unauthorized_controls:
        unsupported_claim_categories.append("unauthorized-control")
    if containment_mentions and not approval_qualifier_present:
        unsupported_claim_categories.append("unqualified-containment")
    if omitted_findings or duplicate_findings:
        unsupported_claim_categories.append("finding-coverage-error")
    return {
        "audit_schema_version": "1.3",
        "json_parse_valid": json_parse_valid,
        "schema_valid": schema_valid,
        "grounding_valid": grounding_valid,
        "known_finding_citations": sorted(cited_findings),
        "unknown_finding_citations": sorted(finding_candidates - known_finding_ids),
        "known_evidence_citations": sorted(cited_evidence),
        "unknown_evidence_citations": sorted(event_candidates - known_evidence_ids),
        "omitted_findings": omitted_findings,
        "duplicate_findings": duplicate_findings,
        "finding_coverage": round(len(cited_findings) / len(known_finding_ids), 6) if known_finding_ids else 1.0,
        "evidence_coverage": round(len(cited_evidence) / len(known_evidence_ids), 6) if known_evidence_ids else 1.0,
        "unsupported_cve_mentions": cve_mentions,
        "absolute_assertions": absolute_assertions,
        "unsupported_security_attribution_mentions": attribution_mentions,
        "containment_action_mentions": containment_mentions,
        "human_approval_qualifier_present": approval_qualifier_present,
        "unqualified_containment_action": bool(containment_mentions) and not approval_qualifier_present,
        "unauthorized_controls": unauthorized_controls,
        "unsupported_claim_categories": unsupported_claim_categories,
        "unsupported_claim_flag": bool(unsupported_claim_categories),
        "word_count": word_count,
        "within_200_word_limit": word_count <= 200,
        "markdown_marker_present": markdown_marker_present,
    }


def audit_free_text(response: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Backward-compatible alias for the symmetric model-response audit."""
    return audit_model_response(response, findings)


class HistoricalOllamaAdvisor:
    """Adapt the original free-text technical prompt to the current evidence pack."""

    def __init__(
        self,
        model: str,
        *,
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 300,
        context_length: int = 4096,
        max_output_tokens: int = 512,
    ):
        if not model.strip():
            raise ValueError("An Ollama model name is required")
        if not 512 <= context_length <= 32_768:
            raise ValueError("Ollama context length must be between 512 and 32768 tokens")
        if not 128 <= max_output_tokens <= 4096:
            raise ValueError("Ollama max output tokens must be between 128 and 4096")
        self.model = model.strip()
        self.base_url = validate_local_ollama_url(base_url)
        self.timeout = timeout
        self.context_length = context_length
        self.max_output_tokens = max_output_tokens

    def analyze(self, findings: list[dict[str, Any]], events: list[TelemetryEvent]) -> dict[str, Any]:
        evidence_index = {item.event_id: item.to_evidence() for item in events}
        evidence_pack = [
            {
                "finding": finding,
                "events": [evidence_index[item] for item in finding["evidence_ids"] if item in evidence_index],
            }
            for finding in findings
        ]
        prompt = f"""Como analista de segurança sênior, forneça uma análise técnica DETALHADA destes achados:

ACHADOS E EVIDÊNCIAS:
{json.dumps(evidence_pack, ensure_ascii=False, sort_keys=True)}

Forneça análise técnica em 3 seções:

1. ANÁLISE DO COMPORTAMENTO OBSERVADO
   - implicações técnicas
   - prioridade de revisão

2. ANÁLISE DE RISCO
   - impacto plausível
   - informações que precisam ser validadas

3. RECOMENDAÇÕES
   - próximos passos defensivos
   - limitações da evidência disponível

Use terminologia técnica de segurança. Máximo 200 palavras. Sem formatação Markdown."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_ctx": self.context_length,
                "num_predict": self.max_output_tokens,
            },
        }
        started = time.perf_counter()
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        body = response.json()
        raw_response = body.get("response", "")
        if not isinstance(raw_response, str) or not raw_response.strip():
            raise ValueError("Ollama returned no free-text response")
        return {
            "raw_response": raw_response,
            "audit": audit_free_text(raw_response, findings),
            "metadata": {
                "model": body.get("model", self.model),
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                "ollama_total_duration_ns": body.get("total_duration"),
                "prompt_eval_count": body.get("prompt_eval_count"),
                "eval_count": body.get("eval_count"),
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "protocol": "reconstructed-2025-free-text",
                "historical_source_commit": HISTORICAL_SOURCE_COMMIT,
                "temperature": 0.7,
                "top_p": 0.9,
                "context_length": self.context_length,
                "max_output_tokens": self.max_output_tokens,
                "request_timeout_seconds": self.timeout,
                "historical_prompt_adapted_to_v2_evidence": True,
            },
        }
