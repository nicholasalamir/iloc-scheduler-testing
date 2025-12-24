import pytest
import sys
import os

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Scanner import Scanner
from io import StringIO


@pytest.fixture
def scanner():
    # Provides a fresh Scanner instance for each test
    return Scanner()


@pytest.fixture
def test_data_dir():
    # Returns path to test data directory
    return os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture
def sample_iloc_file(test_data_dir, tmp_path):
    # Creates a temporary ILOC file for testing
    def _create_file(content):
        file_path = tmp_path / "test.iloc"
        file_path.write_text(content)
        return str(file_path)
    return _create_file
