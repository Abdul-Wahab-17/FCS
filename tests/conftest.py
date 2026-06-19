from __future__ import annotations

import shutil
from pathlib import Path

import pytest


@pytest.fixture()
def rules_path() -> Path:
    return Path("src/severity/parsed_rules.json")


@pytest.fixture()
def labeled_video(tmp_path: Path) -> Path:
    path = tmp_path / "data" / "test" / "Carrying_Overload_with_Forklift"
    path.mkdir(parents=True)
    return path / "clip_001.mp4"


@pytest.fixture(autouse=True)
def clean_pycache() -> None:
    yield
    shutil.rmtree(".pytest_cache", ignore_errors=True)
