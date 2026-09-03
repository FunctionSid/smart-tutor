import pytest
from smarttutor.exam.models import (
    Citation,
    ExamQuestion,
    ExamResult,
    ExamSpec,
    ExamSubmission,
    QuestionResult,
    QuestionValidation,
)


def test_citation_model():
    c = Citation(source="test.pdf", page=2, quote="sample text")
    assert c.source == "test.pdf"
    assert c.page == 2
    assert c.quote == "sample text"


def test_exam_question_model():
    q = ExamQuestion(
        topic="Optics",
        question="What is the critical angle?",
        options=["45 degrees", "61 degrees", "90 degrees", "30 degrees"],
        correct_option="B",
        explanation="Calculated via Snell's Law.",
        citation=Citation(source="optics.pdf", page=1, quote="critical angle is 61"),
        knowledge_point_id="kp_optics_1",
    )
    assert q.correct_option == "B"
    assert len(q.options) == 4
    assert q.difficulty == "medium"


def test_exam_spec_model():
    spec = ExamSpec(
        title="Physics Exam",
        topic="Optics",
        kb_name="optics_kb",
        num_questions=1,
        questions=[
            ExamQuestion(
                topic="Optics",
                question="What is Snell's law?",
                options=["n1 sin1 = n2 sin2", "E = mc2", "F = ma", "V = IR"],
                correct_option="A",
                explanation="Standard refraction formula.",
                citation=Citation(source="doc.pdf", quote="n1 sin1 = n2 sin2"),
                knowledge_point_id="kp_optics_2",
            )
        ],
    )
    assert spec.num_questions == 1
    assert len(spec.questions) == 1
    assert spec.topic == "Optics"


def test_exam_submission_and_result():
    sub = ExamSubmission(answers={"q1": "B"}, time_spent_seconds=45)
    assert sub.answers["q1"] == "B"
    assert sub.time_spent_seconds == 45

    res = ExamResult(
        exam_id="exam_123",
        score=1,
        total=1,
        percentage=100.0,
        time_spent_seconds=45,
        results=[
            QuestionResult(
                question_id="q1",
                question="Question 1",
                options=["A", "B", "C", "D"],
                selected_option="B",
                correct_option="B",
                is_correct=True,
                explanation="Correct explanation.",
                citation=Citation(source="doc.pdf", quote="quote"),
                topic="Optics",
                knowledge_point_id="kp_1",
            )
        ],
        topic_breakdown={"Optics": {"correct": 1, "total": 1}},
    )
    assert res.score == 1
    assert res.percentage == 100.0
