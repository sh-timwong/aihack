
# Backend Structure

This document outlines the backend architecture for the Corporate Conversation Simulation Platform, built upon the Google Agent Development Kit (ADK).

## 1. Core Framework

The backend is built exclusively using the **Google Agent Development Kit (ADK) for Python**. ADK provides the foundational components for defining agents, managing conversations, and orchestrating complex, multi-agent interactions.

## 2. Agent Definitions

The core of the simulation platform is the **Agent Layer**. Each persona and role is implemented as a distinct `LlmAgent` instance.

### 2.1. Persona Agents (Participant Pool)

- **Implementation**: Each persona (e.g., CTO, Product Manager) is a separate `LlmAgent`.
- **Configuration**:
    - `name`: A unique identifier (e.g., `"cto_jack"`, `"pm_bob"`).
    - `model`: Can be configured per-agent (e.g., a more powerful model like `"gemini-1.5-pro"` for a "CTO" agent, and a faster model like `"gemini-2.0-flash"` for others).
    - `description`: A concise summary of the persona's role and key characteristics. This is **critical** for the Orchestrator agent to make delegation decisions. Example: `"Jack, the visionary but risk-averse CTO."`
    - `instruction`: A detailed prompt that defines the agent's personality, goals, concerns, communication style, and knowledge base. This instruction will guide the LLM to respond in character.
    - `tools`: Persona agents can be equipped with tools to simulate specific actions, like fetching mock data or performing a calculation.

### 2.2. Dedicated Observer Agents

- **Implementation**: The Facilitator, NoteTaker, and EmotionalSupport roles are also implemented as specialized `LlmAgent` instances.
- **Configuration**:
    - **NoteTaker Agent**: Will be equipped with tools for summarizing text and extracting key points/action items. Its `instruction` will focus it on listening and recording, not active participation.
    - **Facilitator Agent**: Its `instruction` will guide it to keep the conversation on track, manage time, and interject based on predefined rules or frameworks (e.g., STAR method).
    - **EmotionalSupport Agent**: Its `instruction` will contain prompts focused on empathy, encouragement, and providing constructive, positive feedback.

## 3. Orchestration and Communication

The system follows a hierarchical, orchestrated communication model as described in the project idea.

- **Central Orchestrator**: A root `LlmAgent` acts as the meeting host and orchestrator.
    - It will contain all active agents for a given simulation in its `sub_agents` list.
    - Its `instruction` prompt is the most complex, as it defines the rules of engagement for the entire simulation. It will be responsible for:
        1.  Receiving the user's input.
        2.  Analyzing the input and the current conversation state.
        3.  Delegating the turn to the most appropriate sub-agent (persona or observer) based on their `description`. ADK's `auto_flow` will be leveraged for this.
- **Workflow Agents**: For more structured interactions, `SequentialAgent` or `ParallelAgent` can be used. For example, a post-meeting flow could be a `SequentialAgent` that first calls the `NoteTaker` to generate a summary, and then calls the `EmotionalSupport` agent to deliver feedback.
- **Communication via State**: Agents do not communicate directly. The orchestrator passes context, and agents read/write to a shared `session.state` to access information from previous turns.

## 4. State Management

- **`SessionService`**: A `SessionService` will be used to manage the lifecycle of each conversation simulation.
    - For local development and testing, `InMemorySessionService` will be used.
    - For production, a persistent service like `DatabaseSessionService` (with SQLite or another DB) will be necessary to save and resume sessions.
- **`session.state`**: The session state dictionary will be the "memory" for each meeting. It will store:
    - The current topic and goals of the meeting.
    - Key facts or decisions made in previous turns.
    - Outputs from agents (e.g., the notes from the `NoteTaker`) for other agents to use.
    - `output_key` on agents will be used to automatically save their responses to state.

## 5. Data and API Layer

- **Persona Profiles**: Agent persona details (instructions, descriptions, etc.) will be loaded from external structured files (e.g., YAML or JSON) rather than being hardcoded in Python. This allows for easy creation and editing of new personas without code changes.
- **API Server**: A **FastAPI** web server will wrap the ADK `Runner`. It will expose endpoints for:
    - `POST /simulations`: To start a new simulation, specifying which personas to include.
    - `POST /simulations/{session_id}/message`: To send a message to an ongoing simulation.
    - `GET /simulations/{session_id}/feedback`: To retrieve the final summary and feedback after a session concludes. 