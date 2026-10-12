"""Configuration settings for NexaData AI."""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = BASE_DIR / "datainfo.csv"
LOGO_PATH = BASE_DIR / "NexaData AI_ Ask_Analyze_Discover.png"

# App settings
APP_TITLE = "NexaData AI"
APP_SUBTITLE = "Ask. Analyze. Discover."
APP_ICON = "🧠"

# Default AI Model
# Allows overriding via environment variable or Streamlit secrets
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def get_openai_api_key() -> str:
    """Retrieve OpenAI API key safely from Streamlit secrets or OS environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    
    return os.getenv("OPENAI_API_KEY", "")
