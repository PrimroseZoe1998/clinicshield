import pytest

from scripts.container_smoke import check_runtime_content


def test_runtime_check_allows_only_sample_directories(tmp_path):
    for name in ("lakeview_dental", "southside_counseling", "westside_health"):
        (tmp_path / "samples" / name).mkdir(parents=True)
    check_runtime_content(tmp_path)


@pytest.mark.parametrize("name", ["samples/reports", "data/cache", "docs", ".git"])
def test_runtime_check_rejects_even_empty_development_directories(tmp_path, name):
    (tmp_path / name).mkdir(parents=True)
    with pytest.raises(RuntimeError, match=name):
        check_runtime_content(tmp_path)


def test_runtime_check_names_unexpected_secret_file(tmp_path):
    (tmp_path / ".env").write_text("dummy=test")
    with pytest.raises(RuntimeError, match=r"image: \.env"):
        check_runtime_content(tmp_path)
