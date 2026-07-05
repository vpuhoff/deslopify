from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext, Tool

from deslopify.config import DeslopConfig
from deslopify.models import DeslopResult
from deslopify.pipeline import build_editor_agent, deslop


@dataclass(slots=True)
class DeslopToolDeps:
    """Зависимости для tool remove_ai_traces."""

    config: DeslopConfig


async def remove_ai_traces(ctx: RunContext[DeslopToolDeps], text: str) -> dict[str, Any]:
    """Убирает следы ИИ-генерации из текста и возвращает черновик, критику и финал.

    Args:
        text: Исходный текст с признаками ИИ-генерации («слоп»).

    Returns:
        Словарь с полями finalText, draft, critique, changesSummary, patternsFound,
        tokensConsumed и полным result.
    """
    result = await deslop(text, config=ctx.deps.config)
    return deslop_tool_payload(result)


def deslop_tool_payload(result: DeslopResult) -> dict[str, Any]:
    return {
        "finalText": result.final_text,
        "patternsFound": result.draft.patterns_found,
        "draft": result.draft.draft,
        "critiquePoints": result.critique.critique_points,
        "changesSummary": result.final.changes_summary,
        "tokensConsumed": result.tokens_consumed,
        "result": result.model_dump(by_alias=True),
    }


def create_deslop_tool(config: DeslopConfig | None = None) -> Tool[DeslopToolDeps]:
    """Создаёт Tool для регистрации в любом PydanticAI-агенте."""
    return Tool(remove_ai_traces, takes_ctx=True, name="remove_ai_traces")


def create_deslop_agent(
    *,
    config: DeslopConfig | None = None,
    instructions: str | None = None,
) -> Agent[DeslopToolDeps, str]:
    """Агент-редактор с tool remove_ai_traces для встраивания в пайплайны."""
    cfg = config or DeslopConfig()
    default_instructions = (
        "Ты — редактор-помощник. Когда пользователь просит очеловечить текст, "
        "убрать ИИ-следы или «деслопить» его — вызывай tool remove_ai_traces. "
        "После обработки покажи финальный текст и кратко перечисли главные изменения."
    )

    editor = build_editor_agent(cfg)
    agent: Agent[DeslopToolDeps, str] = Agent(
        editor.model,
        deps_type=DeslopToolDeps,
        instructions=instructions or default_instructions,
        model_settings=editor.model_settings,
    )

    @agent.tool
    async def remove_ai_traces_tool(ctx: RunContext[DeslopToolDeps], text: str) -> dict[str, Any]:
        """Убирает следы ИИ-генерации из текста.

        Args:
            text: Исходный текст с признаками ИИ-генерации.
        """
        return await remove_ai_traces(ctx, text)

    return agent
