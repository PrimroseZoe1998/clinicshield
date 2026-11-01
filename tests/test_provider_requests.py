from types import SimpleNamespace
from pathlib import Path
from fractions import Fraction
import pytest
from app import generate_example
from clinicshield.provider_requests import provider_requests
from clinicshield.report_text import render_assessment_text
from clinicshield.fix_first import rank_actions


def occurrence(rule,details,status="confirmed"):
    return SimpleNamespace(finding=SimpleNamespace(rule=SimpleNamespace(rule_id=rule),
        observation=SimpleNamespace(status=status,evidence=tuple(details.items()))))


def test_backup_request_uses_only_failed_branch_and_keeps_verification_request():
    text=provider_requests([occurrence("R16",{"Q10":"Yes","Q11":"No"})],"assessment")[0]
    assert "controlled restore test" in text
    assert "frequency and separation" not in text
    assert "dated evidence" in text and "cost estimate" in text


@pytest.mark.parametrize("rule,details,expected,absent",[
    ("R20",{"Q20":"Yes","Q24a":"No"},"name the person","document an incident-response plan"),
    ("R21",{"Q21":"No","Q22":"Unknown"},"staff report suspected","notification obligation"),
    ("R21",{"Q21":"Yes","Q22":"No"},"without assuming a breach","staff report suspected"),
])
def test_combined_controls_do_not_invent_other_failures(rule,details,expected,absent):
    text=provider_requests([occurrence(rule,details)],"assessment")[0]
    assert expected in text and absent not in text


def test_unresolved_occurrences_never_become_remediation_requests():
    assert provider_requests([occurrence("R05",{},"needs_review")],"device:A")==[]
    assert provider_requests([occurrence("R05",{},"needs_review"),
        occurrence("R16",{"Q11":"No"})],"assessment")==provider_requests(
        [occurrence("R16",{"Q11":"No"})],"assessment")


def test_cve_and_software_identity_survive_in_request():
    text=provider_requests([occurrence("R01",{"vendor":"Example", "product":"App",
        "version":"1.0", "vulnerability_id":"CVE-2026-12345"})],"device:A")[0]
    assert "device:A / Example / App / 1.0 / CVE-2026-12345" in text
    assert "plan" in text and "before changes" in text


def test_grouped_actions_retain_requests_without_summing_priority():
    base=dict(entity_id="device:A",rule_ids=["R03"],issue_keys=["os"],
        recommendations=["same action"],owners=["IT"],costs=["unknown"],
        points=Fraction(9),effort=3,kev=False,essential_questions=[],touches_phi=True,
        provider_requests=["request 1"])
    other={**base,"rule_ids":["R08"],"issue_keys":["smb"],"provider_requests":["request 2"]}
    actions=rank_actions([base,other])
    assert len(actions)==1 and actions[0]["priority_exact"]=="3"
    assert actions[0]["provider_requests"]==["request 1","request 2"]


@pytest.mark.parametrize("clinic,expected",[("lakeview_dental",65),("southside_counseling",82),("westside_health",80)])
def test_requests_reach_export_with_unchanged_scores(clinic,expected):
    report=generate_example(clinic,30,True)
    assert report["score"]["final"]==expected
    assert report["fix_first"]["actions"]
    for action in report["fix_first"]["actions"]:
        assert action["provider_requests"]
        assert all(action["entity_id"] in text for text in action["provider_requests"])
    text=render_assessment_text(report)
    assert "Copyable provider/lead request:" in text
    assert "dated evidence for reassessment" in text
