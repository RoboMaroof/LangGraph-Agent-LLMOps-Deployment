import pytest
from ingestion.sources import get_documents

def test_invalid_source_type():
    with pytest.raises(ValueError):
        get_documents("invalid", "/some/path")

def test_empty_sql_returns_no_docs(tmp_path):
    db_file = tmp_path / "test.db"
    db_file.write_text("")  # Corrupt file
    with pytest.raises(Exception):
        get_documents("sql", str(db_file))
