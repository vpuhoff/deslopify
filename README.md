# deslopify

Python-библиотека для удаления следов ИИ-генерации в текстах. Повторяет трёхэтапный пайплайн сервиса De-slopatizer: черновик → самокритика → финальная версия.

## Установка

```bash
uv sync
cp .env.example .env   # и пропишите OPENROUTER_API_KEY
```

Ключ OpenRouter можно задать в `.env` — библиотека подхватит его при импорте.
Для явной загрузки через uv: `uv run --env-file .env python test_api.py`.

Альтернатива через pip:

```bash
pip install -e ".[dev]"
export OPENROUTER_API_KEY="sk-or-..."
```

## Быстрый старт

```python
import asyncio
from deslopify import deslop, DeslopConfig

async def main():
    result = await deslop(
        "В современном мире искусственный интеллект играет ключевую роль...",
        config=DeslopConfig(model="google/gemini-2.5-flash"),
    )
    print(result.final_text)
    print(result.tokens_consumed)

asyncio.run(main())
```

Синхронно:

```python
from deslopify import deslop_sync

print(deslop_sync("Ваш текст").final_text)
```

## PydanticAI tool

Tool `remove_ai_traces` можно повесить на любого агента:

```python
from pydantic_ai import Agent
from deslopify import DeslopConfig, DeslopToolDeps, create_deslop_tool

config = DeslopConfig()
agent = Agent(
    "openrouter:google/gemini-2.5-flash",
    deps_type=DeslopToolDeps,
    tools=[create_deslop_tool(config)],
)

result = await agent.run(
    "Убери ИИ-следы из текста: ...",
    deps=DeslopToolDeps(config=config),
)
```

Или использовать готового редактора:

```python
from deslopify import DeslopToolDeps, create_deslop_agent, DeslopConfig

config = DeslopConfig()
agent = create_deslop_agent(config=config)
result = await agent.run(
    "Очеловечь этот абзац: ...",
    deps=DeslopToolDeps(config=config),
)
```

## CLI

```bash
uv run deslopify "Текст для обработки"
uv run python test_api.py --text "Ваш текст"
echo "Текст" | uv run deslopify --json
```

## Модель по умолчанию

`google/gemini-2.5-flash` через OpenRouter — как в оригинальном сервисе.
