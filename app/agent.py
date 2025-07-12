from app.agents.orchestrator import create_orchestrator_agent_v1

# This is the entry point that the ADK web command will look for.
# (EN, TC) 這是 ADK web 命令將尋找的進入點。
root_agent = create_orchestrator_agent_v1() 