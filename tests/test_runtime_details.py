import subprocess
from types import SimpleNamespace
from importlib import metadata
import pytest
from clinicshield import runtime_details as module


def test_reports_dependency_drift_and_effective_host_setting(tmp_path,monkeypatch):
    (tmp_path/"requirements.txt").write_text("streamlit==1.66.1\npyarrow==25.0.1\ncertifi==2026.10.19\n")
    versions={"streamlit":"1.66.1","pyarrow":"24.0.0","certifi":"2026.10.23","pip":"26.3"}
    monkeypatch.setattr(module.metadata,"version",lambda name:versions[name])
    monkeypatch.setattr(module.subprocess,"run",lambda *a,**k:SimpleNamespace(stdout="a"*40,returncode=0))
    data=module.runtime_details(tmp_path,usage_stats=True)
    assert data["packages"]["streamlit"]["matches_pin"] is True
    assert data["packages"]["pyarrow"]["matches_pin"] is False
    assert data["packages"]["certifi"]["matches_pin"] is False
    assert data["packages"]["pip"]["repository_pin"] is None
    assert data["effective_usage_statistics_setting"] is True
    assert data["checkout_commit"]=="a"*40
    assert set(data)=={"checkout_commit","python","effective_usage_statistics_setting","packages"}


@pytest.mark.parametrize("failure",[FileNotFoundError(),subprocess.TimeoutExpired("git",2)])
def test_missing_git_or_timeout_does_not_break_app(tmp_path,monkeypatch,failure):
    def fail(*a,**k): raise failure
    monkeypatch.setattr(module.subprocess,"run",fail)
    assert module.checkout_revision(tmp_path)=="unavailable"


def test_unexpected_git_output_is_not_shown(tmp_path,monkeypatch):
    monkeypatch.setattr(module.subprocess,"run",lambda *a,**k:SimpleNamespace(stdout="private error text",returncode=1))
    assert module.checkout_revision(tmp_path)=="unavailable"


def test_missing_package_and_requirements_are_explicit(tmp_path,monkeypatch):
    def missing(name): raise metadata.PackageNotFoundError(name)
    monkeypatch.setattr(module.metadata,"version",missing)
    monkeypatch.setattr(module,"checkout_revision",lambda root:"unavailable")
    data=module.runtime_details(tmp_path,usage_stats=False)
    assert all(p["installed"]=="unavailable" for p in data["packages"].values())
