from agents.graph_builder import GraphBuilder
from utils.logger import get_logger

logger = get_logger(__name__)


class AgentLoader:
    """
    Instantiates and preloads a GraphBuilder agent into memory.
    Called at application startup.

    Returns:
        GraphBuilder: The initialized agent instance.
    """

    _instance = None

    @classmethod
    def get_agent(cls):
        if cls._instance is None:
            cls._instance = GraphBuilder()
        return cls._instance
