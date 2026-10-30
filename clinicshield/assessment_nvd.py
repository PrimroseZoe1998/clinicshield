from dataclasses import replace
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError, field_validator

from clinicshield.cvss import interpret_cvss
from clinicshield.assessment_evidence_links import validate_evidence_links
from clinicshield.feed_freshness import check_feed_freshness
from clinicshield.feed_models import VulnerabilityRecord
from clinicshield.input_limits import InputError, MAX_JSON_BYTES, validate_upload
from clinicshield.normalization import normalize_name, normalize_version
from clinicshield.nvd_cache import cve_id, load_json, read_nvd_cache, source_time
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


def simple_cpe(value):
    if not isinstance(value, str) or "\\" in value or "?" in value:
        return None
    parts = value.split(":")
    if (len(parts) != 13 or parts[:3] != ["cpe", "2.3", "a"]
            or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", part) or part == "-" for part in parts[3:6])
            or any(part != "*" for part in parts[6:])):
        return None
    return parts


class ReviewedNvdMapping(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    review_status: Literal["reviewed"]
    review_basis: str = Field(strict=True, min_length=1)
    software_entry_id: str = Field(strict=True, min_length=1)
    cve_id: str
    vendor: str = Field(strict=True, min_length=1)
    product: str = Field(strict=True, min_length=1)
    cpe23: str

    @field_validator("cve_id")
    @classmethod
    def validate_cve(cls, value):
        return cve_id(value)

    @field_validator("cpe23")
    @classmethod
    def require_simple_cpe(cls, value):
        if simple_cpe(value) is None:
            raise ValueError("Mapping requires a simple application CPE with an explicit version.")
        return value


def exact_configuration(record, target):
    """Interpret only a single, unnegated OR leaf with no ranges/platform constraints."""
    configs = record.get("configurations")
    if not isinstance(configs, list) or len(configs) != 1 or not isinstance(configs[0], dict):
        return None
    config = configs[0]
    if (set(config) - {"operator", "negate", "nodes"} or config.get("operator", "OR") != "OR"
            or config.get("negate", False) is not False):
        return None
    nodes = config.get("nodes")
    if not isinstance(nodes, list) or len(nodes) != 1 or not isinstance(nodes[0], dict):
        return None
    node = nodes[0]
    if (set(node) - {"operator", "negate", "cpeMatch"} or node.get("operator") != "OR"
            or node.get("negate", False) is not False):
        return None
    matches = node.get("cpeMatch")
    if not isinstance(matches, list) or len(matches) != 1 or not isinstance(matches[0], dict):
        return None
    match = matches[0]
    if (set(match) - {"vulnerable", "criteria", "matchCriteriaId"}
            or match.get("vulnerable") is not True):
        return None
    parts = simple_cpe(match.get("criteria"))
    if parts is None or parts[2:5] != target[2:5]:
        return None
    return parts[5]


def adapt_nvd(mapping, snapshot):
    record = snapshot.record
    status = record.get("vulnStatus")
    affected = exact_configuration(record, simple_cpe(mapping.cpe23))
    state = "rejected" if status == "Rejected" else "active" if status == "Analyzed" and affected else "unknown"
    generated = source_time(snapshot.response["timestamp"])
    if source_time(record["lastModified"]) > generated or source_time(record["published"]) > source_time(record["lastModified"]):
        state = "unknown" if state != "rejected" else state
    basis = (
        "NVD configuration: single exact application leaf. " if affected else
        "NVD configuration is missing or unsupported; do not flatten ranges or logical conditions. "
    )
    return VulnerabilityEvidence(
        software_entry_id=mapping.software_entry_id, record_status=state,
        source_generated_at=generated,
        cvss_context=interpret_cvss(record),
        record=VulnerabilityRecord(
            vulnerability_id=snapshot.cve_id, source=snapshot.source,
            source_url=snapshot.request_url, retrieved_at=snapshot.retrieved_at,
            vendor=mapping.vendor, product=mapping.product,
            version_rule="exact" if affected else "unsupported",
            affected_versions=(affected,) if affected else (),
            version_evidence=basis + "Reviewed mapping: " + mapping.review_basis,
        ),
    )


def load_assessment_nvd(assessment, evidence, directory, allowlist, mapping_data, *, now, max_age):
    mappings = []
    if mapping_data is not None:
        validate_upload(mapping_data, max_bytes=MAX_JSON_BYTES)
        try:
            mappings = TypeAdapter(list[ReviewedNvdMapping]).validate_python(load_json(mapping_data))
        except (ValidationError, ValueError):
            raise InputError("Provide valid reviewed NVD software mapping JSON.") from None
    seen = set()
    software = {f"software:{i}": entry for i, entry in enumerate(assessment.inventory.software, 1)}
    for mapping in mappings:
        identity = (mapping.software_entry_id, mapping.cve_id)
        if identity in seen or mapping.cve_id not in allowlist.cve_ids or mapping.software_entry_id not in software:
            raise InputError("NVD mapping must be unique, allowlisted and linked to a supplied software entry.")
        seen.add(identity)
        entry = software[mapping.software_entry_id]
        target = simple_cpe(mapping.cpe23)
        if (normalize_name(entry.vendor) != normalize_name(mapping.vendor)
                or normalize_name(entry.product) != normalize_name(mapping.product)
                or (normalize_version(entry.version) is not None and normalize_version(entry.version) != target[5])):
            raise InputError("NVD mapping does not match the supplied software identity/version.")
    needed = {mapping.cve_id for mapping in mappings}
    snapshots = {}
    available = 0
    messages = [f"NVD coverage is limited to {len(allowlist.cve_ids)} reviewed allowlisted CVE(s); no automatic software matching."]
    for identifier in allowlist.cve_ids:
        try:
            snapshot = read_nvd_cache(directory / "nvd" / f"{identifier}.json", identifier)
        except (ValueError, OSError):
            snapshot = None
        if snapshot is None:
            messages.append(f"NVD {identifier}: cache unavailable or invalid; coverage unassessed.")
            continue
        available += 1
        retrieval = check_feed_freshness(snapshot.retrieved_at, now=now, max_age=max_age)
        source = check_feed_freshness(source_time(snapshot.response["timestamp"]), now=now, max_age=max_age)
        analysis = "analyzed" if snapshot.record.get("vulnStatus") == "Analyzed" else "rejected" if snapshot.record.get("vulnStatus") == "Rejected" else "requires review"
        messages.append(f"NVD {identifier}: retrieval {retrieval.value}, API response {source.value}; analysis status {analysis}.")
        messages.append(f"NVD {identifier} CVSS context: {interpret_cvss(snapshot.record)}")
        if identifier in needed:
            snapshots[identifier] = snapshot
    messages.append(f"NVD: {available}/{len(allowlist.cve_ids)} allowlisted cache records available. Availability is not applicability.")
    if not mappings:
        messages.append("No reviewed NVD software mappings supplied; no NVD applicability inferred.")
    combined = {key: list(records) for key, records in evidence.vulnerabilities.items()}
    for mapping in mappings:
        if mapping.cve_id not in snapshots:
            continue
        records = combined.setdefault(mapping.software_entry_id, [])
        if any(item.record.vulnerability_id == mapping.cve_id for item in records):
            raise InputError("NVD mapping conflicts with supplied applicability evidence.")
        adapted = adapt_nvd(mapping, snapshots[mapping.cve_id])
        records.append(adapted)
        messages.append(f"NVD {mapping.software_entry_id}/{mapping.cve_id}: supplied mapping loaded; record status {adapted.record_status}; configuration interpretation {adapted.record.version_rule}. Version applicability still requires evaluation.")
    result = replace(evidence, vulnerabilities=combined)
    validate_evidence_links(assessment, result)
    return result, tuple(messages)
