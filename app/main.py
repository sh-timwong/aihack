import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents.orchestrator import create_orchestrator_agent_v1
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def main():
    """
    A simple test script to run the V1 Orchestrator Agent.
    """
    print("Initializing V1 Orchestrator Agent...")
    orchestrator_agent = create_orchestrator_agent_v1()
    print(f"Agent '{orchestrator_agent.name}' created with sub-agent: {[sub.name for sub in orchestrator_agent.sub_agents]}")

    # Setup ADK Runner and Session
    session_service = InMemorySessionService()
    app_name = "corp_sim_v1"
    user_id = "test_user"
    session_id = "session_123"

    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    runner = Runner(
        agent=orchestrator_agent,
        app_name=app_name,
        session_service=session_service
    )

    # Simulate a user query
    query = "As the CTO, what is your biggest concern for our new product launch?"
    print(f"\nUser Query: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
    
    print(f"\nAgent Final Response: {final_response}")

if __name__ == "__main__":
    # Note: If running in a Jupyter/Colab notebook, you might need to run `await main()` directly.
    asyncio.run(main()) 