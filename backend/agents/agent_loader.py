from agents.graph_builder import GraphBuilder
import logging

logger = logging.getLogger(__name__)

agent_instance = None

def preload_agent():
    global agent_instance
    logger.info("⚙️ Preloading GraphBuilder agent...")
    agent_instance = GraphBuilder()
    logger.info("✅ Agent preloaded.")
    return agent_instance