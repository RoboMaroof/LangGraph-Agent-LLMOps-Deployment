from fastapi import APIRouter, Body, HTTPException
import time

from langchain_core.messages import HumanMessage
import agents.agent_loader as loader 
from utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter()

@router.post("/agent/invoke")
async def run_agent(inputs: dict = Body(...)):
    """
    Endpoint to invoke an AI agent with user input.

    Accepts a JSON body with:
        - input (str): The user message to process.
        - model (str, optional): Model configuration string (e.g., 'openai:gpt-4o-mini').
        - session_id (str, optional): Identifier for session-based memory.

    Returns:
        dict: Parsed output from the agent including responses, tools used, etc.

    Raises:
        HTTPException: If input is invalid or agent execution fails.
    """
    # Extract input parameters
    user_input = inputs.get("input", "")
    model_config = inputs.get("model", "openai:gpt-4o-mini")
    session_id = inputs.get("session_id", "default")

    # Handle nested input payloads
    if isinstance(user_input, dict):
        user_input = user_input.get("input", "")

    # Input validation
    if not isinstance(user_input, str) or not user_input.strip():
        raise HTTPException(status_code=400, detail="Field 'input' must be a non-empty string.")

    # Check if the agent instance is initialized
    try:
        agent = loader.AgentLoader.get_agent()
    except Exception as e:
        logger.exception("❌ Agent initialization failed.")
        raise HTTPException(status_code=500, detail="Agent not ready.")

    # Construct message list for the agent
    messages = [HumanMessage(content=user_input)]
    logger.info("💬 Session %s | Model: %s | Input: %s", session_id, model_config, user_input)

    try:
        # Invoke the agent and parse the response
        start = time.time()
        result = agent.invoke_and_parse(messages, session_id=session_id)
        logger.info("✅ Agent response completed in %.2fs", time.time() - start)
        return result
    except Exception as e:
        logger.exception("❌ Agent execution failed for session: %s", session_id)
        raise HTTPException(status_code=500, detail=str(e))