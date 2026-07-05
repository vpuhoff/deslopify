#!/usr/bin/env python3
"""Тестовый скрипт для проверки библиотеки deslopify."""

from __future__ import annotations

import argparse
import json
import sys

from deslopify import DeslopConfig, DeslopResult, deslop_sync

DEFAULT_TEXT = """
В современном быстро меняющемся мире концепция управления временем приобретает все большую актуальность. Ни для кого не секрет, что в условиях постоянного информационного шума и многозадачности сохранение высокой продуктивности становится настоящим вызовом. Важно понимать, что универсального ответа на этот вопрос не существует, однако успешное решение данной проблемы требует комплексного и сбалансированного подхода.
В заключение хочется добавить, что тайм-менеджмент — это не жесткий свод правил, а гибкий инструмент, требующий постоянного анализа. Подводя итог вышесказанному, можно с уверенностью констатировать: осознанный подход к распределению собственных сил неизбежно открывает новые горизонты для саморазвития.
"""


def print_result(result: DeslopResult, *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(result.model_dump(by_alias=True), ensure_ascii=False, indent=2))
        return

    print("\n=== Итог ===")
    print(json.dumps(result.model_dump(by_alias=True), ensure_ascii=False, indent=2))

    print("\n--- Черновик ---")
    print(result.draft.draft or "(пусто)")

    if result.draft.patterns_found:
        print("\nНайденные паттерны:")
        for item in result.draft.patterns_found:
            print(f"  - {item}")

    print("\n--- Критика ---")
    for point in result.critique.critique_points:
        print(f"  - {point}")

    print("\n--- Финальный текст ---")
    print(result.final_text or "(пусто)")

    if result.final.changes_summary:
        print("\nИзменения:")
        for item in result.final.changes_summary:
            print(f"  - {item}")

    print(f"\nВсего токенов: {result.tokens_consumed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Проверка библиотеки deslopify")
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT,
        help="Текст для обработки",
    )
    parser.add_argument(
        "--model",
        default=DeslopConfig().model,
        help="Модель OpenRouter (по умолчанию: google/gemini-2.5-flash)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DeslopConfig().temperature,
        help="Temperature для модели",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenRouter API key (иначе берётся из OPENROUTER_API_KEY)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Вывести только JSON-результат",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config_kwargs: dict[str, object] = {
        "model": args.model,
        "temperature": args.temperature,
    }
    if args.api_key:
        config_kwargs["api_key"] = args.api_key
    config = DeslopConfig(**config_kwargs)

    try:
        config.require_api_key()
    except ValueError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        sys.exit(1)

    preview = args.text[:120] + ("..." if len(args.text) > 120 else "")
    print(f"deslopify ({config.model})")
    print(f"Текст ({len(args.text)} символов): {preview}")
    print("Этапы: draft → critique → final")

    try:
        result = deslop_sync(args.text, config=config)
    except Exception as exc:
        print(f"\nОшибка обработки: {exc}", file=sys.stderr)
        sys.exit(1)

    print_result(result, as_json=args.json)


if __name__ == "__main__":
    main()
