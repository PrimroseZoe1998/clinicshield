"""Synthetic Westside comparison fixture; never apply to real inventory uploads."""
from copy import deepcopy
from dataclasses import replace
from clinicshield.input_limits import InputError
from clinicshield.sample_evidence import build_sample_evidence
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.segmentation_evidence import MedicalSeparationEvidence

NOTICE = (
    "SYNTHETIC POST-FIX SCENARIO ONLY. These changes and verification records are "
    "fictional assumptions for regression testing, not completed work, vendor "
    "support claims, real observations or a forecast of actual score improvement. "
    "Timestamps describe fixture generation. Unassessed source coverage remains unresolved."
)


def build_westside_post_fix(assessment, *, now):
    """Copy the supplied baseline and apply only the declared fictional changes."""
    before = build_sample_evidence("westside_health", assessment, now=now)
    assets = {a.asset_id: a for a in assessment.inventory.assets}
    required = {"WH-MD02", "WH-LT01", "WH-PR01", "WH-SRV01", "WH-SRV02"}
    telnet = [s for s in assessment.inventory.services if s.asset_id == "WH-PR01" and s.service == "telnet" and s.port == 23]
    if (not required <= assets.keys() or len(assets) != 35 or len(telnet) != 1
            or assessment.checklist.answers["Q18"] != "No"
            or assessment.checklist.answers["Q23"] != "No"):
        raise InputError("Use the documented original fictional Westside baseline.")
    changed = deepcopy(assessment)
    changed_assets = {a.asset_id: a for a in changed.inventory.assets}
    support = dict(before.os_support)
    for identifier in ("WH-MD02", "WH-LT01"):
        asset = changed_assets[identifier]
        asset.os_name = "Fictional Supported OS"
        asset.os_version = "synthetic-1"
        asset.notes = NOTICE + " Synthetic replacement/migration assumed; not a real device change."
        support[identifier] = LifecycleEvidence(
            os_name=asset.os_name, os_version=asset.os_version, support_status="supported",
            support_basis=NOTICE, extended_support="not_applicable",
            source_url="https://example.org/clinicshield-synthetic-post-fix",
            retrieved_at=now, source_generated_at=now)
    changed_assets["WH-LT01"].encrypted = "Y"
    changed_assets["WH-MD02"].network_segment = "synthetic-medical-restricted"
    changed.inventory.services = [s for s in changed.inventory.services
        if not (s.asset_id == "WH-PR01" and s.service == "telnet" and s.port == 23)]
    changed.checklist.answers.update({"Q05":"Yes", "Q06":"Yes", "Q11":"Yes",
                                      "Q18":"Unknown", "Q23":"Yes"})
    # Other OS records lack reviewed support evidence; do not assert Q18 Yes.
    for software in changed.inventory.software:
        if software.asset_id == "WH-SRV01":
            software.notes = NOTICE + " A controlled restore test is assumed to pass."
        if software.asset_id == "WH-SRV02":
            software.notes = NOTICE + " Individually attributable accounts are assumed."
    evidence = replace(before, os_support=support, medical_separation={
        "WH-MD02": MedicalSeparationEvidence(asset_id="WH-MD02", separation_verified="Yes",
            evidence_basis=NOTICE + " Effective restricted access is assumed for the fixture.",
            evidence_source="Synthetic regression fixture only", observed_at=now)})
    return changed, evidence
