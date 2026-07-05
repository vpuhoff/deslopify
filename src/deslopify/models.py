from __future__ import annotations

from pydantic import BaseModel, Field


class DraftStage(BaseModel):
    patterns_found: list[str] = Field(
        alias="patternsFound",
        description="Список найденных ИИ-паттернов",
    )
    draft: str = Field(description="Черновая переработка текста")

    model_config = {"populate_by_name": True}


class CritiqueStage(BaseModel):
    critique_points: list[str] = Field(
        alias="critiquePoints",
        description="Что всё ещё выдаёт ИИ в черновике",
    )

    model_config = {"populate_by_name": True}


class FinalStage(BaseModel):
    final_text: str = Field(alias="finalText", description="Итоговая гуманизированная версия")
    changes_summary: list[str] = Field(
        alias="changesSummary",
        description="Сводка главных изменений относительно исходного текста",
    )

    model_config = {"populate_by_name": True}


class DeslopResult(BaseModel):
    original_text: str
    draft: DraftStage
    critique: CritiqueStage
    final: FinalStage
    tokens_consumed: int = Field(description="Суммарное число токенов за все этапы")

    @property
    def final_text(self) -> str:
        return self.final.final_text
