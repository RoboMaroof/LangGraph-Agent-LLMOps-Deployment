from langchain.agents import Tool
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI

from ingestion.index_builder import load_index
from utils.logger import get_logger

logger = get_logger(__name__)

# Module-level cache to avoid rebuilding tools multiple times
_cached_tools = None


def build_tools():
    """
    Constructs and returns a list of tools that can be used by LangChain agents.
    Includes web search tools, academic search tools, and a document retriever
    backed by a vector index (if available).

    Returns:
        list: A list of LangChain-compatible Tool objects.
    """
    tools = []

    # Add API tools
    tools.append(
        WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
        )
    )
    tools.append(
        ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
        )
    )
    tools.append(TavilySearchResults())

    try:
        # Load pre-existing vector index from Qdrant Cloud
        index = load_index()
        if index:
            # Retretiever with LLM reranking
            llm = OpenAI(model="gpt-4o-mini")  # TODO: Make this configurable
            reranker = LLMRerank(top_n=5, llm=llm)

            retriever = VectorIndexRetriever(
                index=index, similarity_top_k=5, postprocessors=[reranker]
            )

            # Wrapper function for retrieval with logging
            def query_debug(query: str):
                logger.debug(f"🧠 Invoked vector retriever with query: {query}")
                nodes = retriever.retrieve(query)
                if not nodes:
                    logger.warning("⚠️ No nodes retrieved from Qdrant.")
                    return "Empty Response"
                for i, node in enumerate(nodes):
                    logger.debug(f"🔍 Node {i+1}: {node.get_text()[:300]}")
                return "\n---\n".join([node.get_text() for node in nodes])

            retriever_tool = Tool(
                name="vector_retriever",
                func=query_debug,
                description=(
                    "Use this tool to search and summarize uploaded documents like PDFs or master theses."
                ),
            )

            tools.append(retriever_tool)
            logger.info("✅ Vector retriever tool loaded.")
        else:
            logger.warning("⚠️ No vector index found. Skipping vector retriever tool.")
    except Exception as e:
        logger.exception("❌ Failed to initialize vector retriever tool: %s", e)

    for tool in tools:
        logger.info("🔌 Tool loaded: %s", getattr(tool, "name", type(tool)))

    return tools


def get_tools():
    """
    Returns a cached list of tools to avoid rebuilding them on every request.

    Returns:
        list: A list of LangChain-compatible Tool objects.
    """
    global _cached_tools
    if _cached_tools is None:
        _cached_tools = build_tools()
    return _cached_tools
