
# core/persona_loader.py
# This utility will load persona data from YAML/JSON files. 
import yaml
from google.adk.agents import LlmAgent
from pathlib import Path

PERSONAS_DIR = Path(__file__).parent.parent / "personas"

def load_persona_agent(persona_name: str) -> LlmAgent:
    """
    Loads a persona from a YAML file and creates an LlmAgent.

    Args:
        persona_name: The name of the persona to load (e.g., "cto_jack").

    Returns:
        An LlmAgent instance configured with the persona's details.
    """
    persona_file = PERSONAS_DIR / f"{persona_name}.yaml"
    if not persona_file.exists():
        raise FileNotFoundError(f"Persona file not found: {persona_file}")

    with open(persona_file, "r") as f:
        persona_data = yaml.safe_load(f)

    return LlmAgent(
        name=persona_data["name"],
        description=persona_data["description"],
        instruction=persona_data["instruction"],
        # For now, we'll use a default model. This can be made configurable later.
        model="gemini-2.0-flash",
    ) 