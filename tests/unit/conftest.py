import pytest

@pytest.fixture(autouse=True)
def _force_not_dry_run(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "false")