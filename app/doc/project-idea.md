## **Project:**

The **Corporate Conversation Simulation Platform** is a sophisticated training tool designed to empower employees by allowing them to practice high-stakes conversations in a safe, controlled, and realistic environment. The platform uses a team of pre-defined, persona-driven AI agents to simulate various workplace scenarios. Users can select which AI personas to interact with, engage in a multi-turn, interactive conversation, and receive detailed, actionable feedback afterward. The system acts as a personal communication coach, helping users build confidence, refine their messaging, and prepare for difficult real-world interactions.

### **System Architecture**

1. #### **Agent Layer**

**Pre-defined Agent Pool:** Each agent has a unique persona, role (e.g., CTO, Product Manager), management style, interests, and concerns.

**Dedicated Role Agents:** Separate agents for facilitator, note-taker, and emotional support, each optimized for their specific function.

2. ##### **Orchestrator/Host**

**Session Manager:** Coordinates meeting setup, agent selection, and session flow.

**Persona Selector:** Lets the user choose which persona join each meeting simulation.

### **Communication Layer**

**Central Orchestrator:** A root agent (the orchestrator) manages the flow of information. It determines which sub-agent should act at each step and passes relevant context to them.

**Context Passing:** Agents do not send messages directly to each other. Instead, the orchestrator or workflow agent (like `SequentialAgent` or `ParallelAgent`) provides each agent with the current context, including user input, prior agent outputs, and session state.

**Session State Management:** Shared state is maintained across the conversation. Agents can read from and write to this state, allowing for persistent memory and information sharing throughout the meeting.

#### **User Interface**

**Conversation UI:** Displays agent chatbot interacting with users and know their goals, pains, and give feedback to them.

**Selection UI:** Allows users to pick a persona to kickstart the meeting simulation.

**Post-Meeting Feedback:** Delivers summaries, action items, and emotional support to the user.

### **Key Concepts**

**Persona-Driven Agents:** Each agent embodies a rich, pre-defined profile for authentic, nuanced interaction.

**Role Specialization:** Dedicated agents for facilitation, note-taking, and emotional support, mirroring real-world meeting dynamics.

**Dynamic Participation:** Agents are selected per meeting, enabling scenario-based simulations.

**Multi-Turn, Multi-Agent Dialogue:** Agents converse over several rounds, maintaining context and reacting to each other.

**Separation of Concerns:** Orchestrator manages flow; agents focus on their roles.

### **Technology Stack**

| Component | Technology/Framework | Purpose |
| :---- | :---- | :---- |
| Agent Framework | Google Agent Development Kit (ADK) (Python) | Agent definition, orchestration |
| Agent Communication | Multi-Agent System (MAS) | Communicate through shared context and workflow orchestration |
| AI Models | Gemini (or other LLMs) | Natural language understanding and response |

### Features

**Scenario-Based Meetings:** The user describes the persona to include in each session of the meeting simulation.

**Dynamic Agent Profiles Creation:** Rich, editable profiles for each persona (name, role, personality, skills, behaviour).

**Automated Note-Taking & Summarization:** Dedicated agent records key points and generates action items.

**Emotional Support Delivery:** After each meeting simulation, a specialized agent offers encouragement and support to the user.

**Session Persistence:** Meeting context, notes, and agent states are maintained throughout the session.

**Modular & Extensible:** Easily add new roles, agents, or meeting scenarios.

#### **Example Conversation Scenario:**

| Name | Role | Personality | Management Style | Capabilities | Interests | Concerns |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Jack | CTO | Visionary, risk-taker | Collaborative | Technical, Strategy | Innovation, Scale | Technical debt |
| Bob | Product Manager | Detail-oriented | Directive | Market analysis | User needs | Budget constraints |

#### 

### **Archiecture Diagram Draft**
---
config:
 theme: default
 layout: fixed
---
flowchart TD
subgraph subGraph0["User-Facing Layer"]
   direction LR
       UI["Conversation Room"]
       User["👤 User"]
       Orchestrator["Orchestrator/Host (Listener)<br><br><b>Role:</b><br>- Gathers user scenario/goals<br>- Manages simulation<br>- Delivers final feedback"]
 end
subgraph subGraph2["<b>Participant Persona Pool</b><br>(Selected for simulation)"]
   direction TB
       CTO["CTO<br>"]
       PM["Product Manager<br>(Bob)"]
 end
subgraph subGraph3["<b>Dedicated Observer</b><br>"]
   direction TB
       Facilitator["Facilitator and framework provider<br>"]
       NoteTaker["Evaluation on conversation performance<br>"]
       EmotionalSupport["Emotional Support<br>"]
 end
subgraph subGraph4["Agent Layer (Google ADK)"]
       AgentLayer("Meeting Simulation<br><i>(Multi-Turn Dialogue)</i>")
       subGraph2
       subGraph3
 end
subgraph subGraph5["Data Storage"]
   direction LR
       AgentProfilesDB["Persona Profiles<br>(JSON/YAML/DB)<br>Personality<br>Goal<br>Pain<br>Behaviour<br>"]
       SessionStateDB["Session State DB"]
 end
subgraph subGraph6["Communication & Foundation"]
   direction TB
       Models["AI Models<br>(Gemini / Other LLMs)"]
       subGraph5
 end
   User --> UI
   UI -- "1- User defines scenario<br>&amp; goal with Orchestrator" --> Orchestrator
   Orchestrator -- "2- Initiates simulation<br>with selected agents" --> AgentLayer
   AgentLayer -- "4- Powered by" --> Models
   subGraph3 -- "6- Generate feedback &amp;<br>suggestions post-meeting" --> Orchestrator
   Orchestrator -- "7- Delivers synthesized<br>feedback to user" --> UI
   style subGraph3 fill:#E1BEE7



### **Summary**

This project enables **realistic, modular, and extensible meeting simulations** using pre-defined, persona-driven agents and multi-agent systems in Google ADK. Each meeting is orchestrated with selected agents, specialized roles, and multi-turn dialogue, providing not only authentic team interactions but also actionable summaries and user-focused emotional support.



