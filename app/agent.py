import yaml
import logging
from collections.abc import AsyncGenerator
from typing import Literal, Optional
from pathlib import Path

from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types
from pydantic import BaseModel, Field

from .config import config

# --- Constants ---
PERSONAS_DIR = Path(__file__).parent / "personas"

# --- Structured Output Models ---
class ProblemSummary(BaseModel):
    """Model representing the problem summary from the Listener phase."""
    
    problem: str = Field(description="The core problem being faced")
    proposed_solution: str = Field(description="The proposed solution")
    key_benefit: str = Field(description="The main benefit of the solution")
    core_challenge: str = Field(description="The primary obstacle to overcome")
    preliminary_advice: str = Field(description="Initial advice for the user")

class SimulationConfig(BaseModel):
    """Model representing the simulation configuration."""
    
    target_persona: str = Field(description="The persona to simulate (e.g., 'Stephen')")
    persona_description: str = Field(description="Description of the persona's characteristics")
    meeting_context: str = Field(description="Context for the simulated meeting")
    max_turns: int = Field(default=10, description="Maximum conversation turns")

class Feedback(BaseModel):
    """Model representing feedback from the Facilitator."""
    
    what_went_well: list[str] = Field(description="List of things that went well")
    areas_for_improvement: list[str] = Field(description="List of areas that need improvement")
    actionable_suggestions: list[str] = Field(description="Specific suggestions for improvement")

# --- Callbacks ---
def phase_transition_callback(callback_context: CallbackContext) -> None:
    """Manages phase transitions and state tracking."""
    session = callback_context._invocation_context.session
    
    # Initialize phase state if not exists
    if "phase_state" not in callback_context.state:
        callback_context.state["phase_state"] = {
            "current_phase": "listener",
            "problem_summary": None,
            "simulation_config": None,
            "conversation_history": [],
            "turn_count": 0
        }
    
    phase_state = callback_context.state["phase_state"]
    
    # Check for phase transition triggers
    user_message = ""
    for event in session.events:
        if event.author == "user" and event.content and event.content.parts:
            user_message = event.content.parts[0].text
            break
    
    # Phase transition logic
    if phase_state["current_phase"] == "listener" and any(word in user_message.lower() for word in ["simulation", "practice", "rehearse"]):
        phase_state["current_phase"] = "coordinator"
        logging.info("Phase transition: listener → coordinator")
    elif phase_state["current_phase"] == "coordinator" and any(word in user_message.lower() for word in ["ready", "start", "begin"]):
        phase_state["current_phase"] = "simulation"
        logging.info("Phase transition: coordinator → simulation")
    elif phase_state["current_phase"] == "simulation" and any(word in user_message.lower() for word in ["end", "stop", "finish"]):
        phase_state["current_phase"] = "feedback"
        logging.info("Phase transition: simulation → feedback")
    
    # Track conversation history
    for event in session.events:
        if event.content and event.content.parts:
            message = event.content.parts[0].text
            phase_state["conversation_history"].append({
                "speaker": event.author,
                "message": message,
                "phase": phase_state["current_phase"]
            })

def simulation_state_callback(callback_context: CallbackContext) -> None:
    """Tracks simulation-specific state and turn counting."""
    session = callback_context._invocation_context.session
    phase_state = callback_context.state.get("phase_state", {})
    
    if phase_state.get("current_phase") == "simulation":
        # Update turn count only during simulation
        phase_state["turn_count"] = phase_state.get("turn_count", 0) + 1
        
        # Track simulation-specific conversation
        if "simulation_history" not in phase_state:
            phase_state["simulation_history"] = []
        
        for event in session.events:
            if event.content and event.content.parts:
                message = event.content.parts[0].text
                if event.author != "Meeting_Orchestrator":  # Don't track orchestrator messages
                    phase_state["simulation_history"].append({
                        "speaker": event.author,
                        "message": message,
                        "turn": phase_state["turn_count"]
                    })

# --- Custom Agents ---
class PhaseController(BaseAgent):
    """Controls phase transitions and manages the overall flow."""
    
    def __init__(self, name: str):
        super().__init__(name=name)
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        phase_state = ctx.session.state.get("phase_state", {})
        current_phase = phase_state.get("current_phase", "listener")
        
        # Check for phase transition triggers
        user_message = ""
        for event in ctx.session.events:
            if event.author == "user" and event.content and event.content.parts:
                user_message = event.content.parts[0].text
                break
        
        # Phase transition logic
        if current_phase == "listener" and "simulation" in user_message.lower():
            # Transition to coordinator phase
            phase_state["current_phase"] = "coordinator"
            yield Event(
                author=self.name,
                content=genai_types.Content(parts=[
                    genai_types.Part(text="**Phase Transition:** Moving from problem definition to simulation setup.")
                ])
            )
        elif current_phase == "coordinator" and "ready" in user_message.lower():
            # Transition to simulation phase
            phase_state["current_phase"] = "simulation"
            yield Event(
                author=self.name,
                content=genai_types.Content(parts=[
                    genai_types.Part(text="**Phase Transition:** Entering simulation mode. The Actor will now respond as Stephen.")
                ])
            )
        elif current_phase == "simulation" and ("end" in user_message.lower() or phase_state.get("turn_count", 0) >= 10):
            # Transition to feedback phase
            phase_state["current_phase"] = "feedback"
            yield Event(
                author=self.name,
                content=genai_types.Content(parts=[
                    genai_types.Part(text="**Phase Transition:** Simulation ended. Moving to feedback and debrief.")
                ])
            )
        else:
            # Continue current phase
            yield Event(author=self.name)

# --- Persona Loading Utility ---
def load_persona_agent(persona_name: str) -> LlmAgent:
    """Loads a persona from a YAML file and creates an LlmAgent."""
    persona_file = PERSONAS_DIR / f"{persona_name}.yaml"
    if not persona_file.exists():
        raise FileNotFoundError(f"Persona file not found: {persona_file}")
    
    with open(persona_file, "r") as f:
        persona_data = yaml.safe_load(f)
    
    return LlmAgent(
        name=persona_data["name"],
        description=persona_data["description"],
        instruction=persona_data["instruction"],
        model=config.persona_model,
        after_agent_callback=simulation_state_callback,
    )

# --- AGENT DEFINITIONS ---

# Phase 1: The Listener - Problem Definition
listener_agent = LlmAgent(
    name="Listener",
    model=config.orchestrator_model,
    description="The Listener agent that helps users define their problem and provides initial guidance.",
    instruction="""
    You are the Listener, the first point of contact for users seeking help with professional challenges.
    
    **Your Role:**
    1. **Listen actively** to the user's problem description
    2. **Ask clarifying questions** to understand the full scope
    3. **Provide a structured summary** of the problem, solution, benefits, and challenges
    4. **Offer preliminary advice** based on the situation
    
    **Response Style:**
    - Be empathetic and supportive
    - Ask follow-up questions to gather complete information
    - Provide a clear, structured summary when the user is ready
    - Give actionable preliminary advice
    
    **When the user mentions wanting to practice or enter simulation:**
    - Acknowledge their readiness
    - Transition them to the Coordinator for simulation setup
    - Do NOT provide detailed simulation advice yourself
    
    Remember: You are the problem definition phase. Focus on understanding and summarizing, not on simulation.
    """,
    after_agent_callback=phase_transition_callback,
)

# Phase 2: The Coordinator - Simulation Setup
coordinator_agent = LlmAgent(
    name="Coordinator",
    model=config.orchestrator_model,
    description="The Coordinator agent that sets up the simulation environment and configures the Actor.",
    instruction="""
    You are the Coordinator, responsible for setting up the simulation environment.
    
    **Your Role:**
    1. **Review the problem summary** from the Listener phase
    2. **Gather persona details** from the user about the person they need to practice with
    3. **Configure the simulation** with the appropriate persona characteristics
    4. **Explain the simulation process** and rules
    5. **Transition to simulation** when the user is ready
    
    **For the Accounting System Scenario:**
    - The target persona is Stephen (CFO)
    - Stephen is traditional, cost-focused, and skeptical of technology
    - He's brilliant with numbers but has limited tech background
    - He's protective of company cash and wary of "IT projects"
    
    **Key Questions to Ask:**
    - "Could you describe Stephen in more detail?"
    - "What is his communication style?"
    - "What are his typical concerns or priorities?"
    - "How does he usually respond to proposals like this?"
    
    **Simulation Rules to Explain:**
    - The Actor will adopt Stephen's persona
    - Maximum 10 conversation turns
    - User can end simulation anytime by saying "End simulation"
    - Facilitator will provide detailed feedback afterward
    
    **When user says they're ready:**
    - Confirm the simulation configuration
    - Explain that Stephen will be direct and challenging
    - Transition to the simulation phase
    """,
    after_agent_callback=phase_transition_callback,
)

# Phase 3: The Actor - Simulation Persona
# Load persona agents for simulation
cto_jack = load_persona_agent("cto_jack")
pm_bob = load_persona_agent("pm_bob")

# Create a dynamic Actor that can adopt different personas
def create_actor_agent(persona_name: str = "stephen") -> LlmAgent:
    """Creates an Actor agent with the specified persona."""
    persona = load_persona_agent(persona_name)
    
    return LlmAgent(
        name=f"Actor_{persona_name.title()}",
        model=config.persona_model,
        description=f"The Actor agent adopting the {persona_name} persona for simulation.",
        instruction=f"""
        You are the Actor in a professional simulation. You are adopting the persona of {persona_name.title()}.
        
        **Your Role:**
        1. **Stay in character** throughout the entire simulation
        2. **Respond naturally** as {persona_name.title()} would
        3. **Maintain consistency** with {persona_name.title()}'s communication style and concerns
        4. **Ask challenging questions** that {persona_name.title()} would realistically ask
        5. **Express concerns** that align with {persona_name.title()}'s priorities
        
        **Response Guidelines:**
        - Use {persona_name.title()}'s typical language and tone
        - Focus on their primary concerns (cost, risk, ROI, etc.)
        - Be appropriately skeptical or supportive based on the persona
        - Keep responses concise and realistic for a business meeting
        
        **Remember:** You are NOT helping the user. You are the person they need to convince.
        """,
        after_agent_callback=simulation_state_callback,
    )

# Default actor agent (Stephen for the accounting scenario)
actor_agent = create_actor_agent("stephen")

# Phase 4: The Facilitator - Feedback and Debrief
facilitator_agent = LlmAgent(
    name="Facilitator",
    model=config.orchestrator_model,
    description="The Facilitator agent that provides detailed feedback on the simulation.",
    instruction="""
    You are the Facilitator, providing detailed feedback and coaching after the simulation.
    
    **Your Role:**
    1. **Review the entire simulation** conversation from the session state
    2. **Provide structured feedback** on what went well and what needs improvement
    3. **Offer specific, actionable suggestions** for improvement
    4. **Help the user understand** how to apply lessons learned
    
    **Feedback Structure:**
    - **What Went Well:** Identify strengths in the user's approach
    - **Areas for Improvement:** Identify specific weaknesses or missed opportunities
    - **Actionable Suggestions:** Provide concrete steps for improvement
    
    **Focus Areas for Stephen (CFO) Scenario:**
    - Did they lead with cost or value?
    - How well did they address ROI concerns?
    - Did they use technical jargon or business language?
    - How did they handle Stephen's skepticism?
    - Did they provide concrete numbers and benefits?
    - How did they respond to challenges and interruptions?
    
    **Tone:** Be constructive and encouraging while being honest about areas for improvement.
    
    **Remember:** Base your feedback on the actual simulation conversation, not generic advice.
    """,
    output_schema=Feedback,
    after_agent_callback=phase_transition_callback,
)

# Custom Orchestrator that manages phase routing
class MeetingOrchestrator(LlmAgent):
    """Custom orchestrator that routes to the appropriate agent based on current phase."""
    
    def __init__(self, name: str):
        super().__init__(name=name, model=config.orchestrator_model)
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        phase_state = ctx.session.state.get("phase_state", {})
        current_phase = phase_state.get("current_phase", "listener")
        
        # Route to appropriate agent based on phase
        if current_phase == "listener":
            # Delegate to listener agent
            async for event in listener_agent._run_async_impl(ctx):
                yield event
        elif current_phase == "coordinator":
            # Delegate to coordinator agent
            async for event in coordinator_agent._run_async_impl(ctx):
                yield event
        elif current_phase == "simulation":
            # Delegate to actor agent
            async for event in actor_agent._run_async_impl(ctx):
                yield event
        elif current_phase == "feedback":
            # Delegate to facilitator agent
            async for event in facilitator_agent._run_async_impl(ctx):
                yield event
        else:
            # Default to listener
            async for event in listener_agent._run_async_impl(ctx):
                yield event

# Main Orchestrator instance
meeting_orchestrator = MeetingOrchestrator(name="Meeting_Orchestrator")

# Root agent for the application
root_agent = meeting_orchestrator 