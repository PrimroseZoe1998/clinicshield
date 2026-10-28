import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from clinicshield import rule_catalog
from clinicshield.input_limits import InputError
from clinicshield.rule_catalog import load_rule_catalog


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def catalog_dir(tmp_path):
    destination = tmp_path / "rules"
    shutil.copytree(ROOT / "rules", destination)
    return destination


def update_rule(path, **changes):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.update(changes)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_loads_complete_repository_catalog():
    rules = load_rule_catalog(ROOT / "rules")

    assert len(rules) == 24
    assert tuple(rule.rule_id for rule in rules) == tuple(
        f"R{number:02d}" for number in range(1, 25)
    )


def test_loads_copied_catalog(catalog_dir):
    assert len(load_rule_catalog(catalog_dir)) == 24


def test_rejects_missing_rule(catalog_dir):
    (catalog_dir / "R24.yaml").unlink()

    with pytest.raises(InputError, match="exactly 24"):
        load_rule_catalog(catalog_dir)


def test_rejects_extra_rule_file(catalog_dir):
    shutil.copyfile(
        catalog_dir / "R24.yaml",
        catalog_dir / "extra.yaml",
    )

    with pytest.raises(InputError, match="exactly 24"):
        load_rule_catalog(catalog_dir)


def test_rejects_duplicate_id_with_missing_id(catalog_dir):
    update_rule(catalog_dir / "R24.yaml", rule_id="R23")

    with pytest.raises(InputError, match="R01 through R24 once"):
        load_rule_catalog(catalog_dir)


def test_rejects_misnamed_rule_file(catalog_dir):
    (catalog_dir / "R24.yaml").rename(catalog_dir / "other.yaml")

    with pytest.raises(InputError, match="filenames"):
        load_rule_catalog(catalog_dir)


def test_accepts_yml_extension(catalog_dir):
    (catalog_dir / "R24.yaml").rename(catalog_dir / "R24.yml")

    assert len(load_rule_catalog(catalog_dir)) == 24


def test_rejects_unregistered_handler(catalog_dir):
    update_rule(
        catalog_dir / "R05.yaml",
        handler="unregistered_handler",
    )

    with pytest.raises(InputError, match="registered handler"):
        load_rule_catalog(catalog_dir)


def test_rejects_wrong_handler_for_rule(catalog_dir):
    update_rule(
        catalog_dir / "R05.yaml",
        handler="telnet_service",
    )

    with pytest.raises(InputError, match="registered handler"):
        load_rule_catalog(catalog_dir)


def test_rejects_wrong_kind(catalog_dir):
    update_rule(catalog_dir / "R05.yaml", kind="checklist")

    with pytest.raises(InputError, match="registered handler"):
        load_rule_catalog(catalog_dir)


def test_rejects_ambiguous_registration(catalog_dir, monkeypatch):
    key = ("R05", "portable_encryption", "technical")
    duplicate_registry = {key: lambda asset: None}
    monkeypatch.setattr(
        rule_catalog,
        "REGISTRIES",
        (*rule_catalog.REGISTRIES, duplicate_registry),
    )

    with pytest.raises(InputError, match="exactly one"):
        load_rule_catalog(catalog_dir)


def test_rejects_noncallable_registration(catalog_dir, monkeypatch):
    key = ("R05", "portable_encryption", "technical")
    registry = next(
        registry
        for registry in rule_catalog.REGISTRIES
        if key in registry
    )
    monkeypatch.setitem(registry, key, None)

    with pytest.raises(InputError, match="registered handler"):
        load_rule_catalog(catalog_dir)


def test_validates_rule_metadata(catalog_dir):
    update_rule(catalog_dir / "R05.yaml", severity="Urgent")

    with pytest.raises(ValidationError):
        load_rule_catalog(catalog_dir)


def test_missing_directory_is_not_a_complete_catalog(tmp_path):
    with pytest.raises(InputError, match="exactly 24"):
        load_rule_catalog(tmp_path / "missing")


def test_loading_does_not_modify_rule_files(catalog_dir):
    original = {
        path.name: path.read_bytes()
        for path in catalog_dir.glob("*.yaml")
    }

    load_rule_catalog(catalog_dir)

    assert {
        path.name: path.read_bytes()
        for path in catalog_dir.glob("*.yaml")
    } == original