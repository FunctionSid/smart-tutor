import pytest
from unittest.mock import AsyncMock, patch
from smarttutor.exam.graph import ExamGraph, ExamGraphState
from smarttutor.exam.models import Citation, ExamQuestion


@pytest.mark.asyncio
async def test_guardrail_rejects_all_of_the_above():
    graph = ExamGraph()
    draft = {
        "question": "Which factor affects scattering?",
        "options": ["Wavelength", "Particle size", "Temperature", "All of the above"],
        "correct_option": "D",
        "explanation": "Everything contributes.",
        "quote": "Scattering depends on wavelength.",
    }
    validation = await graph._call_validate_guardrail(draft, "Scattering depends on wavelength.")
    assert not validation.valid
    assert not validation.no_all_or_none


@pytest.mark.asyncio
async def test_guardrail_rejects_none_of_the_above():
    graph = ExamGraph()
    draft = {
        "question": "What is the speed of light in vacuum?",
        "options": ["100 m/s", "500 m/s", "1000 m/s", "None of the above"],
        "correct_option": "D",
        "explanation": "Light is 3e8.",
        "quote": "Speed of light is constant.",
    }
    validation = await graph._call_validate_guardrail(draft, "Speed of light is constant.")
    assert not validation.valid
    assert not validation.no_all_or_none


@pytest.mark.asyncio
async def test_guardrail_rejects_missing_options():
    graph = ExamGraph()
    draft = {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5"],
        "correct_option": "B",
        "explanation": "Addition.",
        "quote": "2 + 2 = 4",
    }
    validation = await graph._call_validate_guardrail(draft, "2 + 2 = 4")
    assert not validation.valid


@pytest.mark.asyncio
async def test_guardrail_accepts_clean_question():
    graph = ExamGraph()
    passage = "The critical angle of total internal reflection for crown glass in water is 61.0 degrees."
    draft = {
        "question": "What is the critical angle for crown glass immersed in water?",
        "options": ["45.0 degrees", "61.0 degrees", "75.0 degrees", "90.0 degrees"],
        "correct_option": "B",
        "explanation": "Directly stated as 61.0 degrees.",
        "quote": "critical angle of total internal reflection for crown glass in water is 61.0 degrees",
    }
    mock_choice = AsyncMock()
    mock_choice.message.content = '{"approved": true, "reason": "Single correct answer well grounded."}'
    mock_res = AsyncMock()
    mock_res.choices = [mock_choice]

    with patch.object(graph.client.chat.completions, "create", return_value=mock_res):
        validation = await graph._call_validate_guardrail(draft, passage)
        assert validation.valid
        assert validation.has_single_correct
        assert validation.no_all_or_none
        assert validation.citation_grounded
