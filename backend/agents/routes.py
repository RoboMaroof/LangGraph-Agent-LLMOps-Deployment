from fastapi import APIRouter, Body, HTTPException
from langchain_core.messages import HumanMessage
import agents.agent_loader as loader 
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/agent/invoke")
async def run_agent(inputs: dict = Body(...)):
    user_input = inputs.get("input", "")
    model_config = inputs.get("model", "openai:gpt-4o-mini")
    session_id = inputs.get("session_id", "default")

    if isinstance(user_input, dict):
        user_input = user_input.get("input", "")

    if not isinstance(user_input, str) or not user_input.strip():
        raise HTTPException(status_code=400, detail="Field 'input' must be a non-empty string.")

    if loader.agent_instance is None:
        logger.error("❌ Agent instance not initialized.")
        raise HTTPException(status_code=500, detail="Agent not ready.")

    messages = [HumanMessage(content=user_input)]
    logger.info("💬 Session %s | Model: %s | Input: %s", session_id, model_config, user_input)

    try:
        start = time.time()
        result = loader.agent_instance.invoke_and_parse(messages, session_id=session_id)
        logger.info("✅ Agent response completed in %.2fs", time.time() - start)
        return result
    except Exception as e:
        logger.exception("❌ Agent execution failed for session: %s", session_id)
        raise HTTPException(status_code=500, detail=str(e))