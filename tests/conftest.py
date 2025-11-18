import pytest
from app import Config

@pytest.fixture
def config():
    return Config()

# Add more shared fixtures as needed
