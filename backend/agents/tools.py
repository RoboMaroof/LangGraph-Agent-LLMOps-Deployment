import logging
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import Tool

from llama_index.core.postprocessor import LLMRerank
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI

from ingestion.index_builder import load_index

logger = logging.getLogger(__name__)
_cached_tools = None 

def build_tools():
    tools = []

    # 🌐 Web tools
    tools.append(WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)))
    tools.append(ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)))
    tools.append(TavilySearchResults())

    try:
        # 🧠 Load vector index from Qdrant Cloud
        index = load_index()
        if index:
            llm = OpenAI(model="gpt-4o-mini")
            reranker = LLMRerank(top_n=5, llm=llm)

            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=5,
                postprocessors=[reranker]
            )

            query_engine = RetrieverQueryEngine.from_args(retriever)

            retriever_tool = Tool(
                name="vector_retriever",
                func=query_engine.query,
                description="🔍 Search across ingested documents using semantic search and reranking."
            )

            tools.append(retriever_tool)
            logger.info("✅ Vector retriever tool loaded.")
        else:
            logger.warning("⚠️ No vector index found. Skipping vector retriever tool.")
    except Exception as e:
        logger.exception("❌ Failed to initialize vector retriever tool: %s", e)

    for tool in tools:
        logger.info("🔌 Tool loaded: %s", getattr(tool, 'name', type(tool)))

    return tools

def get_tools():
    global _cached_tools
    if _cached_tools is None:
        _cached_tools = build_tools()
    return _cached_tools
