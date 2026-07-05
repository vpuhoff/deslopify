#!/usr/bin/env python3
"""Примеры использования deslopify."""

from __future__ import annotations

import asyncio
import os

from deslopify import DeslopConfig, DeslopToolDeps, create_deslop_agent, deslop


SAMPLE_TEXT = (
    "В современном мире искусственный интеллект играет ключевую роль "
    "в трансформации бизнес-процессов и открывает новые возможности "
    "для компаний любого масштаба."
)


async def direct_pipeline() -> None:
    print("=== Прямой вызов deslop() ===")
    result = await deslop(SAMPLE_TEXT)
    print("Финал:", result.final_text)
    print("Токенов:", result.tokens_consumed)
    print("Паттерны:", result.draft.patterns_found)


async def agent_with_tool() -> None:
    print("\n=== Агент с tool remove_ai_traces ===")
    config = DeslopConfig()
    agent = create_deslop_agent(config=config)
    run = await agent.run(
        "Очеловечь этот текст и покажи результат:\n\n" + SAMPLE_TEXT,
        deps=DeslopToolDeps(config=config),
    )
    print(run.output)


async def main() -> None:
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Задайте OPENROUTER_API_KEY для запуска примеров.")
        return

    await direct_pipeline()
    await agent_with_tool()


if __name__ == "__main__":
    asyncio.run(main())
