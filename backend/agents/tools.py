from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import Tool
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
from ingestion.index_builder import load_index

import logging
logger = logging.getLogger(__name__)

_cached_tools = None 

def build_tools():
    tools = []

    tools.append(WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)))
    tools.append(ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)))
    tools.append(TavilySearchResults())

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
            description="Useful for answering questions from uploaded documents, websites, or SQL databases such as FAQs, company data, policies, etc."
        )
        tools.append(retriever_tool)

    for tool in tools:
        logger.info("🔌 Tool loaded: %s", getattr(tool, 'name', type(tool)))

    return tools

def get_tools():
    global _cached_tools
    if _cached_tools is None:
        _cached_tools = build_tools()
    return _cached_tools