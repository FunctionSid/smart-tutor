import pytest
from pathlib import Path
import tempfile
from smarttutor.exam.models import Citation, ExamQuestion, ExamSpec, ExamSubmission
from smarttutor.exam.service import ExamService
from smarttutor.learning.models import LearningProgress, QuizAttempt
from smarttutor.learning.service import LearningService
from smarttutor.learning.storage import LearningStore


def test_exam_learning_integration_error_and_graduation(tmp_path: Path):
    service = ExamService(exams_dir=tmp_path / "exams")

    question1 = ExamQuestion(
        id="q_optics_1",
        topic="Optics",
        question="What is the critical angle for crown glass in water?",
        options=["45.0 degrees", "61.0 degrees", "75.0 degrees", "90.0 degrees"],
        correct_option="B",
        explanation="61.0 degrees.",
        citation=Citation(source="test.pdf", quote="61.0 degrees"),
        knowledge_point_id="kp_critical_angle",
    )
    question2 = ExamQuestion(
        id="q_optics_2",
        topic="Optics",
        question="What power of wavelength appears in Rayleigh scattering?",
        options=["Second", "Third", "Fourth", "Fifth"],
        correct_option="C",
        explanation="Fourth power.",
        citation=Citation(source="test.pdf", quote="fourth power of wavelength"),
        knowledge_point_id="kp_rayleigh",
    )

    exam = ExamSpec(
        title="Optics Integration Exam",
        topic="Optics",
        kb_name="optics_kb",
        num_questions=2,
        questions=[question1, question2],
    )
    service._save_exam(exam)

    learning_store = LearningStore(root=tmp_path / "learning")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("smarttutor.exam.service.LearningStore", lambda: learning_store)

        sub1 = ExamSubmission(answers={"q_optics_1": "A", "q_optics_2": "C"})
        res1 = service.submit_exam(exam.exam_id, sub1)
        assert res1.score == 1
        assert res1.total == 2
        assert res1.percentage == 50.0

        progress = learning_store.load("exam_optics")
        assert progress is not None
        assert len(progress.error_records) == 1
        assert progress.error_records[0].question_id == "q_optics_1"
        assert progress.error_records[0].status == "active"
        assert len(progress.quiz_attempts) == 2

        sub2 = ExamSubmission(answers={"q_optics_1": "B", "q_optics_2": "C"})
        res2 = service.submit_exam(exam.exam_id, sub2)
        assert res2.score == 2
        assert res2.percentage == 100.0

        updated_progress = learning_store.load("exam_optics")
        assert updated_progress is not None
        assert updated_progress.error_records[0].status == "graduated"
        assert len(updated_progress.quiz_attempts) == 4
