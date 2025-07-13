import os
from dataclasses import dataclass

import google.auth

# To use AI Studio credentials:
# 1. Create a .env file in the /app directory with:
#    GOOGLE_GENAI_USE_VERTEXAI=FALSE
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration
# Try to get project ID from environment first
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

# If not in environment, try to get it from ADC
if not project_id:
    try:
        _, project_id = google.auth.default()
    except (google.auth.exceptions.DefaultCredentialsError, TypeError):
        # Set a default or raise an error if no project_id can be found
        project_id = None

# Set the environment variable only if a project_id was found
if project_id:
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

    orchestrator_model: str = "gemini-1.5-flash"
    persona_model: str = "gemini-1.5-flash"
    max_conversation_turns: int = 10


config = MeetingConfiguration() 