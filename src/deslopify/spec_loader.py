from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

DEFAULT_SPEC_FILENAME = "clean-spec.md"
SECTION_PROCESS = "## Процесс"
SECTION_OUTPUT = "## Формат вывода"
SECTION_EXAMPLE = "## Полный пример"
SECTION_REFERENCE = "## Справка"


def _unescape_skill_text(text: str) -> str:
    text = text.replace(r"\---", "---")
    return re.sub(r"\\(.)", r"\1", text)


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text

    first = lines[0].strip().replace("\\", "")
    if first != "---":
        return text

    for index in range(1, len(lines)):
        if lines[index].strip().replace("\\", "") == "---":
            return "\n".join(lines[index + 1 :])
    return text


def _split_section(
    body: str,
    heading: str,
    next_heading: str | None = None,
    *,
    include_heading: bool = False,
) -> str:
    start = body.find(heading)
    if start == -1:
        return ""
    content_start = start if include_heading else start + len(heading)
    if next_heading:
        end = body.find(next_heading, content_start)
        if end == -1:
            return body[content_start:].strip()
        return body[content_start:end].strip()
    return body[content_start:].strip()


def find_spec_path(explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Файл спеки не найден: {path}")
        return path

    env_path = os.getenv("DESLOPIFY_SPEC_PATH")
    if env_path:
        path = Path(env_path).expanduser().resolve()
        if path.is_file():
            return path

    for base in (Path.cwd(), *Path(__file__).resolve().parents):
        candidate = base / DEFAULT_SPEC_FILENAME
        if candidate.is_file():
            return candidate

    bundled = Path(__file__).resolve().parent / "data" / DEFAULT_SPEC_FILENAME
    if bundled.is_file():
        return bundled

    raise FileNotFoundError(
        f"Не найден {DEFAULT_SPEC_FILENAME}. Укажите путь через DeslopConfig.spec_path "
        "или переменную DESLOPIFY_SPEC_PATH."
    )


@lru_cache(maxsize=4)
def _load_spec_cached(spec_path_str: str) -> tuple[str, str, str, str, str]:
    raw = Path(spec_path_str).read_text(encoding="utf-8")
    body = _unescape_skill_text(_strip_frontmatter(raw)).strip()

    rules = _split_section(body, "# Гуманизатор", SECTION_PROCESS, include_heading=True).strip()
    if not rules:
        raise ValueError(f"В {spec_path_str} не найден раздел «Гуманизатор»")

    process = _split_section(body, SECTION_PROCESS, SECTION_OUTPUT, include_heading=True)
    output_format = _split_section(body, SECTION_OUTPUT, SECTION_EXAMPLE, include_heading=True)
    full_example = _split_section(body, SECTION_EXAMPLE, SECTION_REFERENCE, include_heading=True)
    reference = _split_section(body, SECTION_REFERENCE, include_heading=True)

    return rules, process, output_format, full_example, reference


class HumanizerSpec:
    def __init__(self, spec_path: str | Path | None = None) -> None:
        path = find_spec_path(spec_path)
        rules, process, output_format, full_example, reference = _load_spec_cached(str(path))
        self.path = path
        self.rules = rules
        self.process = process
        self.output_format = output_format
        self.full_example = full_example
        self.reference = reference

    @property
    def system_instruction(self) -> str:
        parts = [self.rules, self.process, self.output_format, self.full_example]
        if self.reference:
            parts.append(self.reference)
        return "\n\n".join(part for part in parts if part)

    @property
    def draft_prompt_template(self) -> str:
        return """Текст для обработки:

{text}

Выполни этапы 1–5 из раздела «Процесс»:
1. Внимательно прочитай текст.
2. Найди все случаи паттернов из инструкции.
3. Перепиши проблемные места.
4. Убедись, что переработанный текст:
   - звучит естественно при чтении вслух;
   - варьирует длину и структуру предложений;
   - использует конкретику вместо абстракций;
   - сохраняет нужный тон исходника (деловой, разговорный, экспертный и т.д.);
   - использует простые конструкции («это», «есть», «у... есть») где уместно.
5. Представь черновой вариант.

Верни JSON с полями patternsFound (список найденных паттернов с кратким пояснением) и draft (черновая переработка)."""

    @property
    def critique_prompt(self) -> str:
        return """Выполни этапы 6–7 из раздела «Процесс» для своего черновика:
6. Спроси себя: «Что в этом тексте всё ещё выдаёт ИИ?»
7. Ответь кратко с оставшимися маркерами (если есть).

Ориентируйся на критерии из раздела «Личность и душа» и эталон из «Полного примера».
Верни JSON с полем critiquePoints — список пунктов."""

    @property
    def final_prompt(self) -> str:
        return """Выполни этапы 8–9 из раздела «Процесс»:
8. Перепиши финальную версию, устранив всё из своей критики.
9. Представь финальную версию.

Также подготовь changesSummary — краткую сводку изменений по сравнению с изначальным текстом пользователя.
Формат сводки как в «Полном примере» (что убрано, что добавлено, как изменился тон).

Верни JSON с полями finalText и changesSummary."""


def get_spec(spec_path: str | Path | None = None) -> HumanizerSpec:
    return HumanizerSpec(spec_path)
