from deslopify.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DeslopConfig
from deslopify.models import CritiqueStage, DeslopResult, DraftStage, FinalStage
from deslopify.pipeline import deslop, deslop_sync
from deslopify.prompts import configure_spec, get_system_instruction
from deslopify.spec_loader import get_spec
from deslopify.tool import (
    DeslopToolDeps,
    create_deslop_agent,
    create_deslop_tool,
    deslop_tool_payload,
    remove_ai_traces,
)

__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "CritiqueStage",
    "DeslopConfig",
    "DeslopResult",
    "DeslopToolDeps",
    "DraftStage",
    "FinalStage",
    "create_deslop_agent",
    "create_deslop_tool",
    "configure_spec",
    "deslop",
    "deslop_sync",
    "deslop_tool_payload",
    "get_spec",
    "get_system_instruction",
    "remove_ai_traces",
]

try:
    from deslopify._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"
