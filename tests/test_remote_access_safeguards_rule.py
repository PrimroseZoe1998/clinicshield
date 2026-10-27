from copy import deepcopy
from pathlib import Path

import pytest

from clinicshield.checklist_input import Checklist, read_checklist
from clinicshield.ingest import read_csv
from clinicshield.input_limits import InputError
from clinicshield.rule_engine import evaluate_service_checklist_rule
from clinicshield.rule_handlers import remote_access_safeguards
from clinicshield.rule_loader import load_rule
from clinicshield.schemas import Service


ROOT = Path(__file__).resolve().parents[1]


def make_service(**changes):
    data = {
        "asset_id": "TEST-SRV01",
        "host": "192.0.2.10",
        "port": 3389,
        "protocol": "tcp",
        "service": "rdp",
        "exposure": "internal",
    }
    data.update(changes)
    return Service(**data)


def make_checklist(answer):
    return Checklist(answers={"Q17": answer}, followups={})


@pytest.mark.parametrize("service_name", ["rdp", "vnc", "ssh", "telnet"])
@pytest.mark.parametrize(
    "answer,expected",
    [
        ("Yes", None),
        ("No", "confirmed"),
        ("Unknown", "needs_review"),
    ],
)
def test_remote_services_and_q17_answers(service_name, answer, expected):
    result = remote_access_safeguards(
        make_service(service=service_name),
        make_checklist(answer),
    )

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.rule_id == "R07"
        assert result.entity_id == "TEST-SRV01"
        assert result.status == expected
        assert dict(result.evidence)["Q17"] == answer


@pytest.mark.parametrize("exposure", ["internal", "internet", "unknown"])
def test_preserves_exposure_without_using_it_as_q17(exposure):
    result = remote_access_safeguards(
        make_service(exposure=exposure),
        make_checklist("No"),
    )

    assert result is not None
    assert dict(result.evidence)["exposure"] == exposure
    assert dict(result.evidence)["Q17"] == "No"


@pytest.mark.parametrize("service_name", ["https", "http", "smb", "other"])
def test_other_services_do_not_trigger(service_name):
    assert remote_access_safeguards(
        make_service(service=service_name),
        make_checklist("No"),
    ) is None


def test_udp_does_not_trigger():
    assert remote_access_safeguards(
        make_service(protocol="udp"),
        make_checklist("No"),
    ) is None


@pytest.mark.parametrize("answer", ["", "no", None, True, [], {}])
def test_rejects_invalid_q17(answer):
    with pytest.raises(InputError, match="valid Q17"):
        remote_access_safeguards(
            make_service(), make_checklist(answer)
        )


def test_requires_q17_for_relevant_service():
    with pytest.raises(InputError, match="valid Q17"):
        remote_access_safeguards(
            make_service(),
            Checklist(answers={}, followups={}),
        )


def test_does_not_invent_service_authentication_details():
    result = remote_access_safeguards(
        make_service(), make_checklist("No")
    )

    assert result is not None
    assert dict(result.evidence) == {
        "asset_id": "TEST-SRV01",
        "host": "192.0.2.10",
        "port": "3389",
        "protocol": "tcp",
        "service": "rdp",
        "exposure": "internal",
        "Q17": "No",
    }


def test_does_not_modify_inputs():
    service = make_service()
    checklist = make_checklist("Unknown")
    original_service = service.model_dump()
    original_checklist = deepcopy(checklist)

    remote_access_safeguards(service, checklist)

    assert service.model_dump() == original_service
    assert checklist == original_checklist


@pytest.mark.parametrize(
    "answer,severity",
    [("No", "High"), ("Unknown", "Info")],
)
def test_yaml_rule_runs_through_engine(answer, severity):
    rule = load_rule(ROOT / "rules" / "R07.yaml")

    finding = evaluate_service_checklist_rule(
        rule, make_service(), make_checklist(answer)
    )

    assert finding is not None
    assert finding.severity == severity
    assert finding.rule.review_status == "draft"


def test_yes_produces_no_engine_finding():
    rule = load_rule(ROOT / "rules" / "R07.yaml")

    assert evaluate_service_checklist_rule(
        rule, make_service(), make_checklist("Yes")
    ) is None


@pytest.mark.parametrize(
    "clinic,expected_assets",
    [
        ("lakeview_dental", {"LV-SRV01"}),
        ("westside_health", set()),
    ],
)
def test_matches_sample_scenarios(clinic, expected_assets):
    rule = load_rule(ROOT / "rules" / "R07.yaml")
    folder = ROOT / "samples" / clinic
    services = read_csv(
        (folder / "services.csv").read_bytes(), "services"
    )
    checklist = read_checklist(
        (folder / "checklist.json").read_bytes(),
        (folder / "followups.json").read_bytes(),
    )
    findings = []

    for service in services:
        finding = evaluate_service_checklist_rule(
            rule, service, checklist
        )
        if finding is not None:
            findings.append(finding)

    assert len(findings) == len(expected_assets)
    assert {
        f.observation.entity_id for f in findings
    } == expected_assets