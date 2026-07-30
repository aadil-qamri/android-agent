"""
Configuration for Android Agent.

All project-wide settings should be defined here.
Nothing else in the project should hardcode these values.
"""

from __future__ import annotations

import os

# -----------------------------------------------------------------------------
# Google Cloud Configuration
# -----------------------------------------------------------------------------

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

if not PROJECT_ID:
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

# -----------------------------------------------------------------------------
# Gemini Model Configuration
# -----------------------------------------------------------------------------

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.5-flash")

# -----------------------------------------------------------------------------
# Application
# -----------------------------------------------------------------------------

APP_NAME = "Android Agent"

VERSION = "0.1.0"

# -----------------------------------------------------------------------------
# Debug
# -----------------------------------------------------------------------------

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
