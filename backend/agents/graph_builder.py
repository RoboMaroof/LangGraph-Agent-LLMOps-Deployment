from typing import Annotated, List
from typing import TypedDict
from collections import defaultdict
import time

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from .tools import get_tools
from utils.logger import get_logger


logger = get_logger(__name__)

# Global memory store for managing per-session chat histories
global_memory_store = defaultdict(InMemoryChatMessageHistory)

# Type definition for agent state used in the graph
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

class GraphBuilder:
    """
    Constructs a conversational graph using LangGraph with support for memory, LLMs, and tools.
    """

    def __init__(self, model_config: str = "openai:gpt-4o-mini"):
        """
        Initializes the graph builder with a selected LLM and associated tools.
        """
        model_type, model_name = model_config.split(":")
        self.tools = get_tools()
        self.llm = self._init_llm(model_type, model_name).bind_tools(tools=self.tools)
        self.tool_node = ToolNode(self.tools)
        self.graph = self._build_graph()

        graph_input_adapter = RunnableLambda(lambda x: {
            "messages": add_messages(x["messages"], x["input"])
        })

        self.graph_with_memory = RunnableWithMessageHistory(
            graph_input_adapter | self.graph,
            self._get_session_memory,
            input_messages_key="input",
            history_messages_key="messages"
        )

    @staticmethod
    def _get_session_memory(session_id: str) -> InMemoryChatMessageHistory:
        """
        Retrieves or creates chat history for a given session.
        """
        return global_memory_store[session_id]

    def _init_llm(self, model_type: str, model_name: str):
        """
        Initializes the selected LLM backend (OpenAI or Groq).
        """
        return ChatGroq(model=model_name) if model_type == "groq" else ChatOpenAI(model=model_name)

    def _llm_tool_node(self, state: AgentState):
        """
        Node logic for LLM invocation with message filtering.
        Filters out invalid or irrelevant messages before invoking the model.
        """
        raw_messages = state.get("messages", [])
        filtered_messages = [
            m for m in raw_messages
            if isinstance(m, (HumanMessage, ToolMessage)) or
            (isinstance(m, AIMessage) and (m.content or m.tool_calls))
        ]

        if not filtered_messages:
            raise ValueError("LLM node received no valid messages after filtering.")

        logger.debug("🤖 Messages going to LLM:\n%s", filtered_messages)
        start = time.time()
        response = self.llm.invoke(filtered_messages)
        logger.info("⏱️ LLM invocation took %.2f seconds", time.time() - start)

        return {"messages": [response]}

    def _build_graph(self):
        """
        Constructs the full agent state graph with conditional logic for tool usage.
        """
        builder = StateGraph(AgentState)
        builder.add_node("tool_calling_llm", self._llm_tool_node)

        # Tool node that invokes tools and updates message history
        def tool_node_with_messages(state: AgentState):
            result = self.tool_node.invoke(state)
            new_messages = result.get("messages", [])
            return {"messages": add_messages(state["messages"], new_messages)}

        # Define edges and transitions in the graph
        builder.add_node("tools", tool_node_with_messages)
        builder.add_edge(START, "tool_calling_llm")
        builder.add_conditional_edges("tool_calling_llm", tools_condition)
        builder.add_edge("tools", "tool_calling_llm")

        return builder.compile()

    def invoke(self, messages: List[AnyMessage]) -> dict:
        """
        Executes the graph with a list of messages, without session memory.
        """
        return self.graph.invoke({"messages": messages})

    def invoke_and_parse(self, messages: List[AnyMessage], session_id: str) -> dict:
        """
        Executes the graph using session-aware memory and parses the response.
        """
        logger.debug("📨 Session %s has %d messages before invoking", session_id, len(messages))

        start = time.time()
        raw_response = self.graph_with_memory.invoke(
            {
                "input": messages,
                "messages": self._get_session_memory(session_id).messages
            },
            config={"configurable": {"session_id": session_id}}
        )
        logger.info("🧠 Full graph invocation took %.2f seconds", time.time() - start)

        return self._parse_response(raw_response)

    def _parse_response(self, response: dict) -> dict:
        """
        Parses the response from the graph into a structured summary including:
        - Final output from the AI
        - Tools used
        - Retrieved data chunks
        - Full intermediate steps
        """
        messages = response.get("messages", [])
        logger.debug("🧩 Parsed messages: %s", messages)

        final_output = None
        tools_used = []
        retrieved_chunks = []
        intermediate_steps = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                intermediate_steps.append({"type": "human", "content": msg.content})

            elif isinstance(msg, AIMessage):
                tool_calls = msg.additional_kwargs.get("tool_calls", [])
                if tool_calls:
                    for call in tool_calls:
                        tool_name = call.get("function", {}).get("name")
                        args = call.get("function", {}).get("arguments")
                        tools_used.append(tool_name)
                        intermediate_steps.append({
                            "type": "ai_tool_call", "tool": tool_name, "args": args
                        })
                else:
                    final_output = msg.content
                    intermediate_steps.append({
                        "type": "ai_final_response", "content": msg.content
                    })

            elif isinstance(msg, ToolMessage):
                tool_name = getattr(msg, "name", None)
                content = msg.content
                artifact = getattr(msg, "artifact", {})

                intermediate_steps.append({
                    "type": "tool_response",
                    "tool": tool_name,
                    "content": content
                })

                if isinstance(artifact, dict) and "results" in artifact:
                    for result in artifact["results"]:
                        retrieved_chunks.append({
                            "tool": tool_name, "type": "result", "data": result
                        })
                else:
                    retrieved_chunks.append({
                        "tool": tool_name, "type": "text", "data": content
                    })
        logger.debug("🛠️ Tools used by LLM: %s", tools_used)
        logger.debug("📦 Retrieved chunks: %s", retrieved_chunks)
        return {
            "final_output": final_output,
            "tools_used": tools_used,
            "retrieved_chunks": retrieved_chunks,
            "intermediate_steps": intermediate_steps,
        }