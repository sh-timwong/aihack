import os
from dataclasses import dataclass

import google.auth

# To use AI Studio credentials:
# 1. Create a .env file in the /app directory with:
#    GOOGLE_GENAI_USE_VERTEXAI=FALSE
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class MeetingConfiguration:
    """Configuration for meeting simulation models and parameters.

    Attributes:
        orchestrator_model (str): Model for orchestrator tasks.
        persona_model (str): Model for persona agents.
        max_conversation_turns (int): Maximum conversation turns allowed.
    """

    orchestrator_model: str = "gemini-2.0-flash"
    persona_model: str = "gemini-2.0-flash"
    max_conversation_turns: int = 10


config = MeetingConfiguration() 