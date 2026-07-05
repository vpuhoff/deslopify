from __future__ import annotations

from deslopify.spec_loader import HumanizerSpec, get_spec

_spec: HumanizerSpec | None = None


def _get_active_spec() -> HumanizerSpec:
    global _spec
    if _spec is None:
        _spec = get_spec()
    return _spec


def configure_spec(spec_path: str | None = None) -> HumanizerSpec:
    """Переключить источник спеки (например, другой clean-spec.md)."""
    global _spec
    _spec = get_spec(spec_path)
    return _spec


def get_system_instruction(spec_path: str | None = None) -> str:
    if spec_path is not None:
        return get_spec(spec_path).system_instruction
    return _get_active_spec().system_instruction


def get_draft_prompt(text: str, spec_path: str | None = None) -> str:
    spec = get_spec(spec_path) if spec_path else _get_active_spec()
    return spec.draft_prompt_template.format(text=text)


def get_critique_prompt(spec_path: str | None = None) -> str:
    spec = get_spec(spec_path) if spec_path else _get_active_spec()
    return spec.critique_prompt


def get_final_prompt(spec_path: str | None = None) -> str:
    spec = get_spec(spec_path) if spec_path else _get_active_spec()
    return spec.final_prompt


def __getattr__(name: str) -> str:
    if name == "SYSTEM_INSTRUCTION":
        return get_system_instruction()
    if name == "CRITIQUE_PROMPT":
        return get_critique_prompt()
    if name == "FINAL_PROMPT":
        return get_final_prompt()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
