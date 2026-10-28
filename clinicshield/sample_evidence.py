from datetime import datetime

from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_input import AssessmentInput
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.input_limits import InputError
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.segmentation_evidence import MedicalSeparationEvidence


SCENARIO_SOURCE = (
    "https://github.com/PrimroseZoe1998/clinicshield/"
    "blob/main/samples/EXPECTED.md"
)

OS_SCENARIOS = {
    "lakeview_dental": {
        "LV-WS01": ("Windows", "10 22H2"),
        "LV-WS02": ("Windows", "10 22H2"),
        "LV-SRV01": ("Windows Server", "2012 R2"),
    },
    "southside_counseling": {},
    "westside_health": {
        "WH-MD02": ("Windows", "7"),
        "WH-LT01": ("Windows", "10 22H2"),
    },
}


def build_sample_evidence(
    clinic: str,
    assessment: AssessmentInput,
    *,
    now: datetime,
) -> AssessmentEvidence:
    """Fictional calibration fixtures only; never use for real uploads."""
    if clinic not in OS_SCENARIOS:
        raise InputError("Choose a documented fictional clinic.")

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Fixture generation time requires a timezone.")

    assets = {
        asset.asset_id: asset for asset in assessment.inventory.assets
    }
    os_support = {}
    passwords = {}
    separation = {}

    for asset_id, expected_identity in OS_SCENARIOS[clinic].items():
        asset = assets.get(asset_id)
        if asset is None or (
            asset.os_name, asset.os_version
        ) != expected_identity:
            raise InputError("Sample OS identity differs from its scenario.")

        os_support[asset_id] = LifecycleEvidence(
            os_name=asset.os_name,
            os_version=asset.os_version,
            support_status="unsupported",
            support_basis=(
                "Fictional scenario assumption for calibration: "
                "this OS is unsupported with no extended coverage. "
                "This is not a live vendor-support determination."
            ),
            extended_support="confirmed_absent",
            source_url=SCENARIO_SOURCE,
            retrieved_at=now,
            source_generated_at=now,
        )

    if clinic == "lakeview_dental":
        router = assets.get("LV-RT01")
        if router is None or router.asset_type != "network_device":
            raise InputError("Sample router differs from its scenario.")

        passwords["LV-RT01"] = DefaultPasswordEvidence(
            asset_id="LV-RT01",
            applicability="Yes",
            default_password_changed="No",
            evidence_basis=(
                "Fictional Lakeview scenario explicitly states that "
                "the default administrator password is unchanged."
            ),
            evidence_source=(
                "samples/lakeview_dental/assets.csv: LV-RT01; "
                "fictional scenario, not an administrator observation"
            ),
            observed_at=now,
        )

    if clinic == "westside_health":
        device = assets.get("WH-MD02")
        if device is None or device.asset_type != "medical_device":
            raise InputError("Sample medical device differs from its scenario.")

        separation["WH-MD02"] = MedicalSeparationEvidence(
            asset_id="WH-MD02",
            separation_verified="No",
            evidence_basis=(
                "Fictional Westside scenario explicitly describes "
                "the ultrasound workstation sharing the workstation network."
            ),
            evidence_source=(
                "samples/EXPECTED.md: Westside Community Health; "
                "fictional scenario, not a network verification"
            ),
            observed_at=now,
        )

    return AssessmentEvidence(
        os_support=os_support,
        default_passwords=passwords,
        medical_separation=separation,
    )