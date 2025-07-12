
# Implementation Plan

This document outlines a phased implementation plan for building the Corporate Conversation Simulation Platform.

## Phase 1: Core Agent and Persona Implementation

**Goal:** Establish the foundational agent personas and a basic single-agent conversation loop.

1.  **Project Setup**:
    -   Initialize a Python project with a virtual environment.
    -   Install `google-adk` and other initial dependencies.
    -   Set up the directory structure (`/app`, `/app/doc`, `/app/agents`, `/app/personas`).

2.  **Define Persona Profiles**:
    -   Create YAML or JSON files in `/app/personas` for at least two initial personas (e.g., `cto_jack.yaml`, `pm_bob.yaml`).
    -   Define key attributes in these files: `name`, `role`, `description`, `instruction`, `interests`, `concerns`.

3.  **Implement a Persona Loader**:
    -   Create a Python utility to load a persona file and instantiate an `LlmAgent` from its contents. This makes agent creation dynamic.

4.  **Develop the Orchestrator Agent (v1)**:
    -   Create a root `LlmAgent` that can load and manage a single persona agent.
    -   For this phase, the Orchestrator will simply pass the user's message directly to the single active persona.

5.  **Initial Testing**:
    -   Use the ADK `Runner` and `InMemorySessionService` in a script to test the conversation flow with one persona.
    -   Verify that the persona agent responds according to its `instruction` prompt.

## Phase 2: Multi-Agent Orchestration and Specialized Roles

**Goal:** Enable a full multi-agent simulation with delegation and specialized observer roles.

1.  **Implement the NoteTaker Agent**:
    -   Define the `NoteTaker` agent.
    -   Create a custom tool using a Python function (`summarize_text`) that it can use.
    -   Instruction should focus the agent on summarizing and extracting action items.

2.  **Implement Facilitator & EmotionalSupport Agents**:
    -   Define the `LlmAgent` for the `Facilitator` and `EmotionalSupport` roles. Their capabilities will be primarily driven by their detailed `instruction` prompts.

3.  **Enhance the Orchestrator Agent (v2)**:
    -   Modify the Orchestrator to accept a list of persona agents to include in a simulation.
    -   Set these active agents as `sub_agents`.
    -   Update the Orchestrator's `instruction` to handle delegation: it should analyze user input and decide whether to handle it directly or transfer control to a sub-agent based on their `description`.

4.  **Test Multi-Agent Delegation**:
    -   Run simulations with multiple agents (e.g., User, CTO, PM, NoteTaker).
    -   Verify that the Orchestrator correctly delegates turns to the appropriate agent.
    -   Use `session.state` to pass the `NoteTaker`'s summary back to the Orchestrator.

## Phase 3: Backend API Server

**Goal:** Expose the agent simulation functionality through a robust API.

1.  **Setup FastAPI**:
    -   Integrate `fastapi` into the project.
    -   Create a `main.py` to house the API application.

2.  **Wrap ADK Runner**:
    -   The FastAPI app will manage a global `Runner` instance.

3.  **Develop API Endpoints**:
    -   `POST /simulations`: Creates a new conversation session. The request body will specify the list of persona names to include. This endpoint will initialize the Orchestrator with the selected agents and a new session ID.
    -   `POST /simulations/{session_id}/message`: Takes user input and runs it through the corresponding agent simulation session. Returns the agent's response.
    -   `GET /simulations/{session_id}/feedback`: To be called at the end of a session. It triggers a final workflow to generate and return the summary from the `NoteTaker` and feedback from the `EmotionalSupport` agent.

4.  **Integrate Persistent Session Service**:
    -   Switch from `InMemorySessionService` to `DatabaseSessionService`.
    -   Set up SQLite for local development to ensure sessions persist between API calls and server restarts.

## Phase 4: UI Integration and Feedback Loop

**Goal:** Connect the backend to a user interface and complete the feedback cycle.

1.  **Build a Simple Frontend**:
    -   Create a basic HTML/JavaScript single-page application that interacts with the backend API.
    -   UI components needed:
        -   A screen to select personas for the simulation.
        -   A chat window to display the conversation.
        -   A text input for the user.
        -   A view to display the final feedback report.

2.  **Connect UI to Backend**:
    -   Implement JavaScript `fetch` calls to the FastAPI endpoints.
    -   Handle the display of multi-turn conversations and the final feedback data.

## Phase 5: Deployment and Scalability

**Goal:** Package and deploy the application for production use.

1.  **Containerize the Application**:
    -   Create a `Dockerfile` for the Python backend.
    -   Ensure it correctly installs dependencies, copies application code, and starts the FastAPI server.

2.  **Deploy to Cloud Service**:
    -   Deploy the container image to a managed service like **Google Cloud Run**.
    -   Configure environment variables (e.g., API keys, database connection strings) in the cloud environment.

3.  **Refine and Evaluate**:
    -   Use the ADK evaluation tools (`adk eval`) to create test sets and measure the quality of agent responses and adherence to personas.
    -   Continuously refine agent instructions and persona profiles based on evaluation results. 