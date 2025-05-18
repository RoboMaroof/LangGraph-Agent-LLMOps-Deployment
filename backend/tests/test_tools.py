from unittest.mock import patch
from agents.tools import get_tools

@patch("agents.tools.load_index")
def test_get_tools_returns_list(mock_load_index):
    mock_load_index.return_value = object()  # Simulate index loaded
    tools = get_tools()
    assert isinstance(tools, list)
