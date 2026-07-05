from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MODEL = "google/gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7


def _load_dotenv() -> None:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]
    seen: set[Path] = set()
    for path in candidates:
        path = path.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not key:
                continue
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_dotenv()


@dataclass(slots=True)
class DeslopConfig:
    """Настройки пайплайна de-slop."""

    model: str = DEFAULT_MODEL
    api_key: str | None = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    temperature: float = DEFAULT_TEMPERATURE
    app_url: str | None = None
    app_title: str = "deslopify"
    spec_path: str | None = field(default_factory=lambda: os.getenv("DESLOPIFY_SPEC_PATH"))

    def require_api_key(self) -> str:
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY не задан. Укажите api_key в DeslopConfig, "
                "положите ключ в .env или установите переменную окружения OPENROUTER_API_KEY."
            )
        return self.api_key
