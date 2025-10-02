"""
Pytest configuration and fixtures for TRIZ tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_problem():
    """Provide a sample problem statement"""
    return "Reduce weight of automotive component while maintaining structural strength"


@pytest.fixture
def complex_problem():
    """Provide a complex multi-faceted problem"""
    return """
    Manufacturing line needs to:
    - Increase throughput by 50%
    - Reduce energy consumption by 30%
    - Improve quality (reduce defects from 3% to 0.5%)
    - Handle 5 product variants instead of 2
    - Reduce maintenance downtime from 10% to 5%
    """
