from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

from clinicshield import nvd_cache, nvd_refresh
from clinicshield.assessment_evidence import AssessmentEvidence
from clinicshield.assessment_input import read_assessment
from clinicshield.assessment_nvd import load_assessment_nvd
from clinicshield.matching import MatchStatus
from clinicshield.nvd_cache import NVD_URL, NvdAllowlist, NvdSnapshot, read_nvd_cache, write_nvd_cache
from clinicshield.nvd_refresh import NvdClient, NvdBudgetExceeded, refresh_nvd_allowlist
from clinicshield.vulnerability_matching import evaluate_applicability

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 29, 21, tzinfo=timezone.utc)
CVE = "CVE-2026-12345"
CPE = "cpe:2.3:a:example_vendor:practice_manager:1.0:*:*:*:*:*:*:*"


def response_data():
    return {"resultsPerPage": 1, "startIndex": 0, "totalResults": 1,
            "format": "NVD_CVE", "version": "2.0", "timestamp": NOW.isoformat(),
            "vulnerabilities": [{"cve": {
                "id": CVE, "sourceIdentifier": "synthetic@example.org", "vulnStatus": "Analyzed",
                "published": (NOW-timedelta(days=10)).isoformat(), "lastModified": NOW.isoformat(),
                "descriptions": [{"lang": "en", "value": "Synthetic testing only."}],
                "references": [], "metrics": {"futureMetric": [{"preserve": True}]},
                "configurations": [{"nodes": [{"operator": "OR", "negate": False,
                    "cpeMatch": [{"vulnerable": True, "criteria": CPE, "matchCriteriaId": "synthetic"}]}]}],
            }}]}


def snapshot(data=None):
    return NvdSnapshot(cve_id=CVE, request_url=f"{NVD_URL}?cveId={CVE}", retrieved_at=NOW,
                       response=data if data is not None else response_data())


def allowlist(ids=None):
    return NvdAllowlist(review_status="reviewed", review_basis="Synthetic test only.", cve_ids=ids if ids is not None else [CVE])


@pytest.mark.parametrize("ids", [["../outside"], [CVE,CVE], [f"CVE-2026-{n:04}" for n in range(51)]])
def test_rejects_bad_duplicate_or_large_allowlist(ids):
    with pytest.raises(ValueError):
        allowlist(ids)


def test_cache_preserves_complete_source_including_unknown_metadata(tmp_path):
    data=response_data()
    data["vulnerabilities"][0]["cve"]["configurations"][0]["nodes"][0]["cpeMatch"][0]["versionEndIncluding"]="2.0"
    path=tmp_path/"record.json"
    write_nvd_cache(path,snapshot(data))
    assert read_nvd_cache(path,CVE).response==data
    assert read_nvd_cache(tmp_path/"absent",CVE) is None


@pytest.mark.parametrize("change", ["empty", "wrong_id", "wrong_url", "future_schema", "count", "naive_retrieval"])
def test_cache_rejects_unexpected_identity_or_envelope(change):
    data=response_data()
    kwargs={"cve_id":CVE,"request_url":f"{NVD_URL}?cveId={CVE}","retrieved_at":NOW,"response":data}
    if change=="empty": data["vulnerabilities"]=[]
    if change=="wrong_id": data["vulnerabilities"][0]["cve"]["id"]="CVE-2026-9999"
    if change=="wrong_url": kwargs["request_url"]="https://example.org"
    if change=="future_schema": data["version"]="3.0"
    if change=="count": data["totalResults"]=2
    if change=="naive_retrieval": kwargs["retrieved_at"]=NOW.replace(tzinfo=None)
    with pytest.raises(ValueError): NvdSnapshot(**kwargs)


def test_failed_replace_preserves_old_cache_and_removes_temporary(tmp_path,monkeypatch):
    path=tmp_path/"record.json"
    path.write_bytes(b"previous")
    def fail(*args): raise OSError("replace failed")
    monkeypatch.setattr(nvd_cache.os,"replace",fail)
    with pytest.raises(OSError): write_nvd_cache(path,snapshot())
    assert path.read_bytes()==b"previous"
    assert list(tmp_path.iterdir())==[path]


class FakeTime:
    value=0
    def clock(self): return self.value
    def sleep(self,seconds): self.value+=seconds


class HttpResponse:
    def __init__(self,status=200,headers=None,data=None):
        self.status_code=status
        self.headers=headers or {}
        self.data=json.dumps(data if data is not None else response_data()).encode()
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def raise_for_status(self):
        if self.status_code>=400: raise requests.HTTPError(response=self)
    def iter_content(self,chunk_size): yield self.data


def client_with(events,budget=600):
    clock=FakeTime()
    starts=[]
    def get(url,**kwargs):
        assert url==f"{NVD_URL}?cveId={CVE}"
        assert kwargs["allow_redirects"] is False
        assert kwargs["stream"] is True
        starts.append(clock.value)
        event=events.pop(0)
        if isinstance(event,Exception): raise event
        return event
    return NvdClient(clock=clock.clock,sleep=clock.sleep,now=lambda:NOW,get=get,budget_seconds=budget),starts


def test_requests_and_retries_share_spacing_and_respect_retry_after():
    client,starts=client_with([HttpResponse(429,{"Retry-After":"25"}),HttpResponse(),HttpResponse()])
    client.download(CVE); client.download(CVE)
    assert starts==[0,25,35]


def test_network_retry_and_three_attempt_limit():
    client,starts=client_with([requests.Timeout(),requests.ConnectionError(),requests.Timeout()])
    with pytest.raises(requests.Timeout): client.download(CVE)
    assert len(starts)==3
    assert all(b-a>=10 for a,b in zip(starts,starts[1:]))


@pytest.mark.parametrize("status", [302,400,403,404])
def test_nonretryable_status_not_retried(status):
    client,starts=client_with([HttpResponse(status)])
    with pytest.raises((ValueError,requests.HTTPError)): client.download(CVE)
    assert len(starts)==1


def test_large_retry_after_stops_without_sleeping_past_budget():
    client,starts=client_with([HttpResponse(429,{"Retry-After":"10000"})],budget=60)
    with pytest.raises(NvdBudgetExceeded): client.download(CVE)
    assert starts==[0]


def test_last_retry_after_is_respected_before_next_cve():
    client,starts=client_with([HttpResponse(503),HttpResponse(503),HttpResponse(429,{"Retry-After":"50"}),HttpResponse()])
    with pytest.raises(requests.HTTPError): client.download(CVE)
    client.download(CVE)
    assert starts[-1]-starts[-2]>=50


def test_download_size_limit(tmp_path,monkeypatch):
    monkeypatch.setattr(nvd_refresh,"MAX_NVD_BYTES",10)
    client,_=client_with([HttpResponse()])
    with pytest.raises(ValueError,match="size limit"): client.download(CVE)


def test_refresh_failure_preserves_last_valid_record(tmp_path):
    path=tmp_path/f"{CVE}.json"
    write_nvd_cache(path,snapshot())
    original=path.read_bytes()
    client,_=client_with([HttpResponse(404)])
    assert refresh_nvd_allowlist(allowlist(),tmp_path,client=client)[0]["outcome"]=="failed"
    assert path.read_bytes()==original


def assessment(version="1.0"):
    folder=ROOT/"samples/lakeview_dental"
    result=read_assessment(**{name+"_json":(folder/f"{name}.json").read_bytes() for name in ("checklist","followups")},
        **{name+"_csv":(folder/f"{name}.csv").read_bytes() for name in ("assets","software","services")})
    result.inventory.software[0]=result.inventory.software[0].model_copy(update={"version":version})
    return result


def mapping():
    return {"review_status":"reviewed","review_basis":"Synthetic test only.","software_entry_id":"software:1",
            "cve_id":CVE,"vendor":"Example Dental Vendor","product":"Practice Manager","cpe23":CPE}


def adapted(tmp_path,data=None,version="1.0",now=NOW):
    write_nvd_cache(tmp_path/"nvd"/f"{CVE}.json",snapshot(data))
    supplied=assessment(version)
    evidence,messages=load_assessment_nvd(supplied,AssessmentEvidence(),tmp_path,allowlist(),json.dumps([mapping()]).encode(),now=now,max_age=timedelta(days=8))
    item=evidence.vulnerabilities["software:1"][0]
    match=evaluate_applicability(supplied.inventory.software[0],item,entity_id="software:1",now=now,max_age=timedelta(days=8))
    return item,match,messages


def test_exact_simple_configuration_can_match(tmp_path):
    item,match,_=adapted(tmp_path)
    assert match.status is MatchStatus.MATCH
    assert item.record_status=="active"


@pytest.mark.parametrize("condition",["range","and","negate","environment","multiple","no_analysis","missing"])
def test_complex_or_unanalyzed_configuration_requires_review(tmp_path,condition):
    data=response_data(); record=data["vulnerabilities"][0]["cve"]
    config=record["configurations"][0]; node=config["nodes"][0]
    if condition=="range": node["cpeMatch"][0]["versionEndExcluding"]="2.0"
    if condition=="and": config["operator"]="AND"
    if condition=="negate": node["negate"]=True
    if condition=="environment": node["cpeMatch"][0]["vulnerable"]=False
    if condition=="multiple": config["nodes"].append(deepcopy(node))
    if condition=="no_analysis": record["vulnStatus"]="Awaiting Analysis"
    if condition=="missing": del record["configurations"]
    _,match,_=adapted(tmp_path,data)
    assert match.status is MatchStatus.NEEDS_REVIEW


def test_unknown_inventory_version_never_confirmed(tmp_path):
    _,match,_=adapted(tmp_path,version="Unknown")
    assert match.status is MatchStatus.NEEDS_REVIEW


def test_different_affected_version_is_nonmatch(tmp_path):
    data=response_data()
    data["vulnerabilities"][0]["cve"]["configurations"][0]["nodes"][0]["cpeMatch"][0]["criteria"]=CPE.replace(":1.0:",":2.0:")
    _,match,_=adapted(tmp_path,data)
    assert match.status is MatchStatus.NO_MATCH


@pytest.mark.parametrize("condition",["stale","future","rejected"])
def test_age_and_rejection_never_confirm_active_gap(tmp_path,condition):
    data=response_data()
    now=NOW+timedelta(days=9) if condition=="stale" else NOW-timedelta(days=1) if condition=="future" else NOW
    if condition=="rejected": data["vulnerabilities"][0]["cve"]["vulnStatus"]="Rejected"
    _,match,_=adapted(tmp_path,data,now=now)
    assert match.status is (MatchStatus.NO_MATCH if condition=="rejected" else MatchStatus.NEEDS_REVIEW)


def test_availability_alone_creates_no_applicability_and_no_network(tmp_path,monkeypatch):
    write_nvd_cache(tmp_path/"nvd"/f"{CVE}.json",snapshot())
    def forbidden(*args,**kwargs): pytest.fail("Assessment must stay offline")
    monkeypatch.setattr(requests.sessions.Session,"request",forbidden)
    evidence,messages=load_assessment_nvd(assessment(),AssessmentEvidence(),tmp_path,allowlist(),None,now=NOW,max_age=timedelta(days=8))
    assert not evidence.vulnerabilities
    assert any("Availability is not applicability" in m for m in messages)


@pytest.mark.parametrize("condition",["orphan","unlisted","duplicate","draft","wrong_product"])
def test_bad_mapping_rejected_without_any_request(tmp_path,condition):
    row=mapping()
    if condition=="orphan": row["software_entry_id"]="software:99"
    if condition=="unlisted": row["cve_id"]="CVE-2026-9999"
    if condition=="draft": row["review_status"]="draft"
    if condition=="wrong_product": row["product"]="Other"
    with pytest.raises(ValueError):
        load_assessment_nvd(assessment(),AssessmentEvidence(),tmp_path,allowlist(),json.dumps([row,row] if condition=="duplicate" else [row]).encode(),now=NOW,max_age=timedelta(days=8))


def test_invalid_missing_and_oversized_cache_are_not_treated_as_safe(tmp_path,monkeypatch):
    path=tmp_path/"nvd"/f"{CVE}.json"
    path.parent.mkdir()
    path.write_text('{"broken":true}')
    evidence,messages=load_assessment_nvd(assessment(),AssessmentEvidence(),tmp_path,allowlist(),None,now=NOW,max_age=timedelta(days=8))
    assert not evidence.vulnerabilities
    assert any("unavailable or invalid" in message for message in messages)
    monkeypatch.setattr(nvd_cache,"MAX_NVD_BYTES",2)
    with pytest.raises(ValueError,match="size limit"): read_nvd_cache(path,CVE)


def test_duplicate_json_keys_and_nonfinite_values_rejected():
    for data in [b'{"a":1,"a":2}',b'{"value":NaN}']:
        with pytest.raises(ValueError): nvd_cache.load_json(data)


def test_allowlist_requires_review_and_bounded_file(tmp_path):
    path=tmp_path/"allowlist.json"
    path.write_text(json.dumps({"review_status":"draft","review_basis":"test","cve_ids":[CVE]}))
    with pytest.raises(ValueError): nvd_cache.read_nvd_allowlist(path)
    path.write_bytes(b" "*(64*1024+1))
    with pytest.raises(ValueError,match="size limit"): nvd_cache.read_nvd_allowlist(path)


def test_api_response_freshness_not_old_record_modification_time(tmp_path):
    data=response_data()
    data["vulnerabilities"][0]["cve"]["lastModified"]=(NOW-timedelta(days=9)).isoformat()
    _,match,_=adapted(tmp_path,data)
    assert match.status is MatchStatus.MATCH


def test_existing_applicability_is_not_silently_overwritten(tmp_path):
    write_nvd_cache(tmp_path/"nvd"/f"{CVE}.json",snapshot())
    supplied=assessment()
    args=(supplied,AssessmentEvidence(),tmp_path,allowlist(),json.dumps([mapping()]).encode())
    evidence,_=load_assessment_nvd(*args,now=NOW,max_age=timedelta(days=8))
    with pytest.raises(ValueError,match="conflicts"):
        load_assessment_nvd(supplied,evidence,*args[2:],now=NOW,max_age=timedelta(days=8))


def test_end_to_end_offline_report_with_supported_nvd_evidence(tmp_path,monkeypatch):
    import app
    from clinicshield.kev_cache import KevSnapshot, write_kev_cache
    from clinicshield.report_text import render_assessment_text
    data = response_data()
    data["vulnerabilities"][0]["cve"]["metrics"] = {"cvssMetricV31": [{
        "source": "synthetic@example.org", "type": "Primary", "cvssData": {
            "version": "3.1", "baseScore": 9.8, "baseSeverity": "CRITICAL",
            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}}]}
    write_nvd_cache(tmp_path/"nvd"/f"{CVE}.json",snapshot(data))
    write_kev_cache(tmp_path/"kev.json",KevSnapshot(retrieved_at=NOW,catalog={
        "catalogVersion":"2026.10.29","dateReleased":NOW,"count":0,"vulnerabilities":[]}))
    monkeypatch.setattr(app,"read_nvd_allowlist",lambda path:allowlist())
    def forbidden(*args,**kwargs): pytest.fail("Complete assessment must remain offline")
    monkeypatch.setattr(requests.sessions.Session,"request",forbidden)
    folder=ROOT/"samples/lakeview_dental"
    uploads={name+"_json":(folder/f"{name}.json").read_bytes() for name in ("checklist","followups")}
    uploads.update({name+"_csv":(folder/f"{name}.csv").read_bytes() for name in ("assets","software","services")})
    uploads["software_csv"]=uploads["software_csv"].replace(b"Practice Manager,Unknown,",b"Practice Manager,1.0,")
    report=app.generate_uploaded(uploads,30,cache_directory=tmp_path,nvd_mappings=json.dumps([mapping()]).encode())
    assert any("R02" in finding["rule_ids"] and finding["status"]=="confirmed_from_supplied_evidence" for finding in report["findings"])
    text=render_assessment_text(report)
    assert "NVD coverage is limited to 1 reviewed allowlisted CVE(s)" in text
    assert "Availability is not applicability" in text
    assert "Synthetic test only" in text
    details = [item["details"] for finding in report["findings"]
               for item in finding["evidence"] if item["rule_id"] == "R02"]
    assert any('"base_score": 9.8' in item["cvss_context"] for item in details)
    assert "synthetic@example.org" in text
    assert "not recalculated from vectors" in text


def test_http_date_retry_after_is_honored():
    from email.utils import format_datetime
    value=format_datetime(NOW+timedelta(seconds=20),usegmt=True)
    client,starts=client_with([HttpResponse(429,{"Retry-After":value}),HttpResponse()])
    client.download(CVE)
    assert starts==[0,20]


def test_exhausted_run_does_not_request_remaining_ids(tmp_path):
    calls=[]
    def fail(identifier):
        calls.append(identifier)
        raise NvdBudgetExceeded("budget exhausted")
    results=refresh_nvd_allowlist(allowlist([CVE,"CVE-2026-9999"]),tmp_path,client=SimpleNamespace(download=fail))
    assert calls==[CVE]
    assert len(results)==2
    assert all(row["outcome"]=="failed" for row in results)


def test_mutated_nested_record_is_revalidated_before_replacing_cache(tmp_path):
    path=tmp_path/"record.json"
    path.write_text("previous")
    value=snapshot()
    value.record["id"]="CVE-2026-9999"
    with pytest.raises(ValueError): write_nvd_cache(path,value)
    assert path.read_text()=="previous"


@pytest.mark.parametrize("condition", ["unknown_version", "unsupported", "stale"])
def test_critical_cvss_does_not_confirm_unresolved_applicability(tmp_path, condition):
    data = response_data()
    data["vulnerabilities"][0]["cve"]["metrics"] = {"cvssMetricV31": [{
        "source": "synthetic@example.org", "type": "Primary", "cvssData": {
            "version": "3.1", "baseScore": 9.8, "baseSeverity": "CRITICAL",
            "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}}]}
    if condition == "unsupported":
        data["vulnerabilities"][0]["cve"]["configurations"] = []
    now = NOW + timedelta(days=9) if condition == "stale" else NOW
    evidence, match, _ = adapted(tmp_path, data, now=now)
    if condition == "unknown_version":
        supplied = assessment()
        supplied.inventory.software[0].version = "Unknown"
        match = evaluate_applicability(supplied.inventory.software[0],
            evidence, entity_id="software:1",
            now=now, max_age=timedelta(days=8))
    assert match.status is MatchStatus.NEEDS_REVIEW
    assert '"base_score": 9.8' in evidence.cvss_context
