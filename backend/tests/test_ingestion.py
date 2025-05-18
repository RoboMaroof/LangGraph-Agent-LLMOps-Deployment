import pytest
from ingestion.index_builder import create_index, load_index

def test_create_index_with_invalid_source_type():
    with pytest.raises(ValueError):
        create_index("invalid_type", "/fake/path")

def test_load_index_returns_index():
    index = load_index()
    assert index is not None
