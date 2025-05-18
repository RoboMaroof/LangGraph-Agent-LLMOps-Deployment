from agents.graph_builder import GraphBuilder
from langchain_core.messages import HumanMessage

def test_graph_builder_basic_flow():
    gb = GraphBuilder()
    messages = [HumanMessage(content="What is LangChain?")]
    result = gb.invoke_and_parse(messages, session_id="test123")
    assert "final_output" in result
