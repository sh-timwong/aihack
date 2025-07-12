
# agetns/orchestrator.py
# This file will contain the logic for the root Orchestrator Agent. 
from google.adk.agents import LlmAgent
from ..core.persona_loader import load_persona_agent

def create_orchestrator_agent_v1() -> LlmAgent:
    """
    Creates the V1 Orchestrator agent.

    This version loads a single persona (e.g., cto_jack) and sets it as a sub-agent.
    Its primary instruction is to delegate tasks to its sub-agent.
    """
    # Load a specific persona to act as the single participant for now.
    cto_agent = load_persona_agent("cto_jack")

    orchestrator = LlmAgent(
        name="Orchestrator",
        description="The main orchestrator for the conversation simulation.",
        instruction="You are the orchestrator of a meeting. Your role is to receive the user's message and pass it to the participant in the meeting. The participant is in your sub_agents list. You must delegate the task to them.",
        sub_agents=[cto_agent],
        model="gemini-2.0-flash",
    )
    return orchestrator 


#     from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm
# from ..core.persona_loader import load_persona_agent

# def create_orchestrator_agent_v1() -> LlmAgent:
#     """
#     Creates the V1 Orchestrator agent.

#     This version loads a single persona (e.g., cto_jack) and sets it as a sub-agent.
#     Its primary instruction is to delegate tasks to its sub-agent.
#     """
#     # Load a specific persona to act as the single participant for now.
#     cto_agent = load_persona_agent("cto_jack")

#     orchestrator = LlmAgent(
#         name="Orchestrator",
#         description="The main orchestrator for the conversation simulation.",
#         instruction="You are the orchestrator of a meeting. Your role is to receive the user's message and pass it to the participant in the meeting. The participant is in your sub_agents list. You must delegate the task to them.",
#         sub_agents=[cto_agent],
#         model=LiteLlm(model="vertex-ai/gemini-2.0-flash"),
#     )
#     return orchestrator 