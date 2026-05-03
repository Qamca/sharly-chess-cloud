import pytest


@pytest.fixture(autouse=True)
def setup_page():
    """Override the root setup_page for unit tests — no browser needed."""
    return None
