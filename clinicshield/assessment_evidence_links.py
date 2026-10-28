from clinicshield.application_evidence import ApplicationSupportEvidence
from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_input import AssessmentInput
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.input_limits import InputError
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.segmentation_evidence import MedicalSeparationEvidence
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


def validate_evidence_links(
    assessment: AssessmentInput,
    evidence: AssessmentEvidence,
) -> None:
    """Reject orphaned or incorrectly associated assessment evidence."""
    asset_ids = {
        asset.asset_id for asset in assessment.inventory.assets
    }
    software_ids = {
        f"software:{index}"
        for index in range(1, len(assessment.inventory.software) + 1)
    }

    asset_sources = (
        (evidence.os_support, LifecycleEvidence),
        (evidence.default_passwords, DefaultPasswordEvidence),
        (evidence.medical_separation, MedicalSeparationEvidence),
    )

    for records, expected_type in asset_sources:
        for key, record in records.items():
            if key not in asset_ids:
                raise InputError("Evidence references an unknown asset.")
            if not isinstance(record, expected_type):
                raise InputError("Asset evidence has an unsupported type.")

            if isinstance(
                record,
                (DefaultPasswordEvidence, MedicalSeparationEvidence),
            ) and record.asset_id != key:
                raise InputError("Asset evidence key does not match its record.")

    for key, record in evidence.application_support.items():
        if key not in software_ids:
            raise InputError("Evidence references an unknown software entry.")
        if not isinstance(record, ApplicationSupportEvidence):
            raise InputError("Application evidence has an unsupported type.")
        if record.software_entry_id != key:
            raise InputError("Application evidence key does not match its record.")

    for key, records in evidence.vulnerabilities.items():
        if key not in software_ids:
            raise InputError("Evidence references an unknown software entry.")

        for record in records:
            if not isinstance(record, VulnerabilityEvidence):
                raise InputError("Vulnerability evidence has an unsupported type.")
            if record.software_entry_id != key:
                raise InputError(
                    "Vulnerability evidence key does not match its record."
                )