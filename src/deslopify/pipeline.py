from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import RunUsage

from deslopify.config import DeslopConfig
from deslopify.models import CritiqueStage, DeslopResult, DraftStage, FinalStage
from deslopify.prompts import (
    configure_spec,
    get_critique_prompt,
    get_draft_prompt,
    get_final_prompt,
    get_system_instruction,
)


def _build_model(config: DeslopConfig) -> OpenRouterModel:
    provider_kwargs: dict[str, str] = {"api_key": config.require_api_key()}
    if config.app_url:
        provider_kwargs["app_url"] = config.app_url
    if config.app_title:
        provider_kwargs["app_title"] = config.app_title

    return OpenRouterModel(
        config.model,
        provider=OpenRouterProvider(**provider_kwargs),
    )


def _build_agent(config: DeslopConfig) -> Agent[None, object]:
    if config.spec_path:
        configure_spec(config.spec_path)
    return Agent(
        _build_model(config),
        instructions=get_system_instruction(config.spec_path),
        model_settings=ModelSettings(temperature=config.temperature),
    )


def build_editor_agent(config: DeslopConfig | None = None) -> Agent[None, object]:
    """Базовый редакторский агент с системным промптом deslopify."""
    return _build_agent(config or DeslopConfig())


def _result_usage(result: object) -> RunUsage:
    usage = getattr(result, "usage", None)
    if usage is None:
        return RunUsage()
    return usage() if callable(usage) else usage


def _usage_total(usage: RunUsage) -> int:
    if usage.total_tokens:
        return usage.total_tokens
    return usage.input_tokens + usage.output_tokens


async def deslop(text: str, config: DeslopConfig | None = None) -> DeslopResult:
    """Трёхэтапная обработка текста: черновик → критика → финал."""
    if not text or not text.strip():
        raise ValueError("text не может быть пустым")

    cfg = config or DeslopConfig()
    agent = _build_agent(cfg)
    usage = RunUsage()

    draft_result = await agent.run(
        get_draft_prompt(text, cfg.spec_path),
        output_type=DraftStage,
    )
    usage += _result_usage(draft_result)
    draft = draft_result.output

    critique_result = await agent.run(
        get_critique_prompt(cfg.spec_path),
        output_type=CritiqueStage,
        message_history=draft_result.all_messages(),
    )
    usage += _result_usage(critique_result)
    critique = critique_result.output

    final_result = await agent.run(
        get_final_prompt(cfg.spec_path),
        output_type=FinalStage,
        message_history=critique_result.all_messages(),
    )
    usage += _result_usage(final_result)
    final = final_result.output

    return DeslopResult(
        original_text=text,
        draft=draft,
        critique=critique,
        final=final,
        tokens_consumed=_usage_total(usage),
    )


def deslop_sync(text: str, config: DeslopConfig | None = None) -> DeslopResult:
    """Синхронная обёртка над deslop()."""
    import asyncio

    return asyncio.run(deslop(text, config=config))
