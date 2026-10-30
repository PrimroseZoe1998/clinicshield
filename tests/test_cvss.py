from copy import deepcopy
import json
import pytest
from clinicshield.cvss import interpret_cvss

VECTOR = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"


def record(score=9.8, rating="CRITICAL"):
    return {"metrics": {"cvssMetricV31": [{"source": "synthetic@example.org",
        "type": "Primary", "cvssData": {"version": "3.1", "vectorString": VECTOR,
        "baseScore": score, "baseSeverity": rating}}]}}


@pytest.mark.parametrize("score,rating", [(0,"NONE"),(.1,"LOW"),(3.9,"LOW"),
    (4,"MEDIUM"),(6.9,"MEDIUM"),(7,"HIGH"),(8.9,"HIGH"),(9,"CRITICAL"),(10,"CRITICAL")])
def test_source_band_boundaries(score,rating):
    result=json.loads(interpret_cvss(record(score,rating)))
    assert result["status"] == "available"
    assert result["assessments"][0]["severity"] == rating


@pytest.mark.parametrize("value", [True, "9.8", -1, 11, 9.81, float("nan"), float("inf"), None])
def test_bad_scores_are_review_not_zero(value):
    result=json.loads(interpret_cvss(record(value)))
    assert result["status"] == "requires_review"
    assert not result["assessments"]


@pytest.mark.parametrize("vector", [VECTOR+"/AV:N", VECTOR.replace("/A:H", ""),
    VECTOR.replace("AV:N", "AV:X"), VECTOR.replace("3.1", "4.0"), None])
def test_bad_vectors_remain_review(vector):
    data=record();data["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"]=vector
    assert json.loads(interpret_cvss(data))["status"] == "requires_review"


def test_preserves_multiple_sources_and_does_not_mutate_or_choose_highest():
    data=record();second=record(7,"HIGH")["metrics"]["cvssMetricV31"][0]
    second["source"]="other@example.org";second["type"]="Secondary"
    data["metrics"]["cvssMetricV31"].append(second)
    before=deepcopy(data);result=json.loads(interpret_cvss(data))
    assert data == before
    assert [a["base_score"] for a in result["assessments"]] == [9.8,7]
    assert "not recalculated" in result["limits"]


def test_optional_metrics_and_any_order():
    data=record();data["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"] = (
        "CVSS:3.1/A:H/I:H/C:H/S:U/UI:N/PR:N/AC:L/AV:N/E:F/RL:X")
    assert json.loads(interpret_cvss(data))["status"] == "available"


@pytest.mark.parametrize("data", [{}, {"metrics":{}}, {"metrics":None}])
def test_missing_is_not_zero(data):
    assert "not a zero" in interpret_cvss(data)


@pytest.mark.parametrize("metrics", [[], {"cvssMetricV40": [{}]}, {"cvssMetricV31":None},
    {"cvssMetricV31":[None]}, {"cvssMetricV31":[]}])
def test_malformed_and_unsupported_visible(metrics):
    assert "review" in interpret_cvss({"metrics":metrics})


def test_conflicting_severity_rejected():
    assert not json.loads(interpret_cvss(record(9.8,"LOW")))["assessments"]
