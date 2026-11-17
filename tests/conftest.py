import copy
import shutil
from pathlib import Path

import pytest

from greenprints.config import load_config

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "sample_shipments.csv"


@pytest.fixture(scope="session")
def cfg():
    """The real project config (real WARM factors and profiles)."""
    return load_config(ROOT)


@pytest.fixture
def cfg_copy(cfg):
    return copy.deepcopy(cfg)


@pytest.fixture
def sample_project(tmp_path):
    """A throwaway project folder: real config + the synthetic fixture CSV."""
    shutil.copytree(ROOT / "config", tmp_path / "config")
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    shutil.copyfile(FIXTURE, raw / "master_shipments.csv")
    return tmp_path
