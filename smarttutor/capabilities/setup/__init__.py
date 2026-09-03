"""Setup loop capability — SmartTutor inspecting and changing its own configuration."""

from smarttutor.capabilities.setup.capability import SetupCapability
from smarttutor.capabilities.setup.tools import SETUP_TOOL_NAMES, SETUP_TOOL_TYPES

__all__ = ["SETUP_TOOL_NAMES", "SETUP_TOOL_TYPES", "SetupCapability"]
