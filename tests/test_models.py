from deslopify.models import CritiqueStage, DeslopResult, DraftStage, FinalStage
from deslopify.spec_loader import get_spec


def test_deslop_result_final_text_property():
    result = DeslopResult(
        original_text="исходник",
        draft=DraftStage(patternsFound=["канцелярит"], draft="черновик"),
        critique=CritiqueStage(critiquePoints=["сухо"]),
        final=FinalStage(finalText="финал", changesSummary=["сократил"]),
        tokens_consumed=100,
    )
    assert result.final_text == "финал"
    dumped = result.model_dump(by_alias=True)
    assert dumped["final"]["finalText"] == "финал"


def test_spec_loader_loads_full_humanizer_rules():
    spec = get_spec()
    instruction = spec.system_instruction

    assert "Раздувание значимости" in instruction
    assert "является важным/ключевым/значимым этапом" in instruction
    assert "Я до сих пор не знаю" in instruction
    assert "Внимательно прочитай текст" in instruction
    assert "Отличный вопрос!" in instruction


def test_stage_prompts_reference_spec_process():
    spec = get_spec()

    assert "этапы 1–5" in spec.draft_prompt_template
    assert "звучит естественно при чтении вслух" in spec.draft_prompt_template
    assert "Что в этом тексте всё ещё выдаёт ИИ?" in spec.critique_prompt
    assert "changesSummary" in spec.final_prompt
    assert "Полном примере" in spec.final_prompt
