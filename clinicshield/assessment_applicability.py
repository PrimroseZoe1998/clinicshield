from dataclasses import replace
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, TypeAdapter, ValidationError

from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_evidence_links import validate_evidence_links
from clinicshield.assessment_input import AssessmentInput
from clinicshield.input_limits import InputError, MAX_JSON_BYTES, validate_upload
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


class ReviewedApplicability(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    review_status: Literal["reviewed"]
    review_basis: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]
    evidence: VulnerabilityEvidence


def load_reviewed_applicability(
    assessment: AssessmentInput, evidence: AssessmentEvidence, data: bytes,
) -> AssessmentEvidence:
    """Accept reviewed source records; existing matchers decide applicability."""
    validate_upload(data, max_bytes=MAX_JSON_BYTES)
    try:
        records = TypeAdapter(list[ReviewedApplicability]).validate_json(data)
    except ValidationError:
        raise InputError("Provide a valid reviewed CVE applicability JSON list.") from None
    entries = {}
    seen = set()
    for reviewed in records:
        item = reviewed.evidence
        key = item.software_entry_id
        identity = (key, item.record.vulnerability_id)
        if identity in seen:
            raise InputError("Duplicate CVE applicability for one software entry.")
        if key in evidence.vulnerabilities:
            raise InputError("Uploaded applicability conflicts with existing evidence.")
        seen.add(identity)
        source = item.record.model_copy(update={
            "version_evidence": (
                item.record.version_evidence + " Review basis: " + reviewed.review_basis
            ).strip(),
        })
        entries.setdefault(key, []).append(item.model_copy(update={"record": source}))
    combined = replace(evidence, vulnerabilities={**evidence.vulnerabilities, **entries})
    validate_evidence_links(assessment, combined)
    return combined
