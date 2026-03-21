"""Pytest configuration and shared fixtures for ArchGuard tests."""

import sys
from pathlib import Path

import pytest

# Add src directory to path so we can import archguard
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory.

    Returns:
        Path to tests/fixtures
    """
    return project_root / "tests" / "fixtures"


@pytest.fixture
def sample_architectures_dir(fixtures_dir: Path) -> Path:
    """Return path to sample architectures fixtures.

    Returns:
        Path to sample_architectures directory
    """
    sample_dir = fixtures_dir / "sample_architectures"
    sample_dir.mkdir(parents=True, exist_ok=True)
    return sample_dir


@pytest.fixture
def sample_code_dir(fixtures_dir: Path) -> Path:
    """Return path to sample code fixtures.

    Returns:
        Path to sample_code directory
    """
    sample_dir = fixtures_dir / "sample_code"
    sample_dir.mkdir(parents=True, exist_ok=True)
    return sample_dir


@pytest.fixture
def expected_results_dir(fixtures_dir: Path) -> Path:
    """Return path to expected results fixtures.

    Returns:
        Path to expected_results directory
    """
    result_dir = fixtures_dir / "expected_results"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def pytest_configure(config) -> None:
    """Configure pytest with custom markers.

    Args:
        config: pytest configuration object
    """
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow-running")


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing.

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Path to temporary file
    """
    temp_file = tmp_path / "temp_test.txt"
    temp_file.write_text("")
    return temp_file


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing.

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Path to temporary directory
    """
    return tmp_path
