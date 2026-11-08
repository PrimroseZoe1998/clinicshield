from copy import deepcopy
import pytest
import app
from clinicshield.findings_table import finding_rows, ordered_findings, CONFIRMED
from clinicshield.scoring import SEVERITY_POINTS


@pytest.mark.parametrize("clinic",list(app.CLINICS.values()))
def test_all_findings_evidence_and_stable_filter_references(clinic):
    report=app.generate_example(clinic,30,True)
    original=deepcopy(report)
    rows=finding_rows(report)
    assert len(rows)==len(report["findings"])
    for row,finding in zip(rows,ordered_findings(report)):
        assert row["Entity"]==finding["scoring_entity_id"]
        for evidence in finding["evidence"]:
            assert evidence["source_entity_id"] in row["Evidence"]
            assert evidence["rule_id"] in row["Evidence"]
    confirmed=finding_rows(report,"Confirmed findings")
    review=finding_rows(report,"Needs review")
    assert len(confirmed)+len(review)==len(rows)
    assert set(r["Ref"] for r in rows)==set(r["Ref"] for r in confirmed+review)
    assert all(r["Status"]=="Needs review" for r in review)
    assert report==original


def test_sort_separates_review_and_uses_severity_points_and_deterministic_ties():
    base=app.generate_example("lakeview_dental",30)["findings"][0]
    findings=[]
    for status,severity,points,entity in [("needs_review","Critical",99,"a"),(CONFIRMED,"High",1,"z"),(CONFIRMED,"Critical",1,"c"),(CONFIRMED,"High",3,"b"),(CONFIRMED,"High",3,"a")]:
        f=deepcopy(base)
        f.update(status=status,severity=severity,exposure_points=points,scoring_entity_id=entity)
        findings.append(f)
    report={"findings":findings}
    assert [f["scoring_entity_id"] for f in ordered_findings(report)]==["c","a","b","z","a"]
    assert ordered_findings(report)==ordered_findings({"findings":list(reversed(findings))})


def test_empty_findings_and_zero_point_review_are_explicit():
    assert finding_rows({"findings":[]})==[]
    report=app.generate_example("lakeview_dental",30)
    review=finding_rows(report,"Needs review")
    assert review
    assert all(row["Status"]=="Needs review" for row in review)
