#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from deslopify import DeslopConfig, deslop_sync


def main() -> None:
    parser = argparse.ArgumentParser(description="De-slop текста через OpenRouter")
    parser.add_argument("text", nargs="?", help="Текст для обработки")
    parser.add_argument("--model", default=DeslopConfig().model, help="Модель OpenRouter")
    parser.add_argument("--json", action="store_true", help="Вывести полный JSON-результат")
    args = parser.parse_args()

    text = args.text
    if not text:
        text = sys.stdin.read().strip()
    if not text:
        parser.error("передайте text аргументом или через stdin")

    result = deslop_sync(text, config=DeslopConfig(model=args.model))

    if args.json:
        print(json.dumps(result.model_dump(by_alias=True), ensure_ascii=False, indent=2))
    else:
        print(result.final_text)
        print(f"\n[токенов: {result.tokens_consumed}]", file=sys.stderr)


if __name__ == "__main__":
    main()
