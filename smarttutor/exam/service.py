from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any, List, Optional

from smarttutor.exam.graph import ExamGraph, ExamGraphState
from smarttutor.exam.models import (
    ExamQuestion,
    ExamResult,
    ExamSpec,
    ExamSubmission,
    QuestionResult,
)
from smarttutor.learning.models import ErrorType, LearningProgress, QuizAttempt
from smarttutor.learning.service import LearningService
from smarttutor.learning.storage import LearningStore
from smarttutor.services.path_service import get_path_service


class ExamService:
    def __init__(self, exams_dir: Optional[Path] = None) -> None:
        self.root = exams_dir or (get_path_service().get_workspace_dir() / "exams")
        self.attempts_dir = self.root / "attempts"
        self.root.mkdir(parents=True, exist_ok=True)
        self.attempts_dir.mkdir(parents=True, exist_ok=True)
        self.learning_service = LearningService()

    async def create_exam(
        self,
        topic: str,
        kb_name: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        time_limit_minutes: Optional[int] = None,
        llm_selection: dict[str, str] | None = None,
    ) -> ExamSpec:
        state = ExamGraphState(
            topic=topic,
            kb_name=kb_name,
            num_questions=num_questions,
            difficulty=difficulty,
            time_limit_minutes=time_limit_minutes,
        )
        exam = await ExamGraph(llm_selection=llm_selection).execute(state)
        self._save_exam(exam)
        return exam

    def _save_exam(self, exam: ExamSpec) -> None:
        file_path = self.root / f"{exam.exam_id}.json"
        file_path.write_text(exam.model_dump_json(indent=2), encoding="utf-8")

    def get_exam(self, exam_id: str, hide_answers: bool = True) -> Optional[ExamSpec]:
        file_path = self.root / f"{exam_id}.json"
        if not file_path.exists():
            return None
        data = json.loads(file_path.read_text(encoding="utf-8"))
        exam = ExamSpec.model_validate(data)
        if not hide_answers:
            return exam

        sanitized_questions = []
        for q in exam.questions:
            sanitized_q = q.model_copy(deep=True)
            sanitized_q.correct_option = "A"
            sanitized_q.explanation = ""
            sanitized_q.citation.quote = ""
            sanitized_questions.append(sanitized_q)

        return exam.model_copy(update={"questions": sanitized_questions})

    def list_exams(self) -> List[dict[str, Any]]:
        exams = []
        for p in self.root.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                exams.append({
                    "exam_id": data.get("exam_id"),
                    "title": data.get("title"),
                    "topic": data.get("topic"),
                    "kb_name": data.get("kb_name"),
                    "num_questions": len(data.get("questions", [])),
                    "time_limit_minutes": data.get("time_limit_minutes"),
                    "created_at": data.get("created_at"),
                })
            except Exception:
                continue
        exams.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return exams

    def submit_exam(
        self,
        exam_id: str,
        submission: ExamSubmission,
        user_id: str = "default",
    ) -> ExamResult:
        file_path = self.root / f"{exam_id}.json"
        if not file_path.exists():
            raise ValueError(f"Exam {exam_id} not found.")

        raw_data = json.loads(file_path.read_text(encoding="utf-8"))
        exam = ExamSpec.model_validate(raw_data)

        score = 0
        total = len(exam.questions)
        results: List[QuestionResult] = []
        topic_breakdown: dict[str, dict[str, int]] = {}

        learning_store = LearningStore()

        for q in exam.questions:
            sel = submission.answers.get(q.id)
            is_correct = sel is not None and sel.strip().upper() == q.correct_option
            if is_correct:
                score += 1

            t_name = q.topic
            if t_name not in topic_breakdown:
                topic_breakdown[t_name] = {"correct": 0, "total": 0}
            topic_breakdown[t_name]["total"] += 1
            if is_correct:
                topic_breakdown[t_name]["correct"] += 1

            results.append(
                QuestionResult(
                    question_id=q.id,
                    question=q.question,
                    options=q.options,
                    selected_option=sel,
                    correct_option=q.correct_option,
                    is_correct=is_correct,
                    explanation=q.explanation,
                    citation=q.citation,
                    topic=q.topic,
                    knowledge_point_id=q.knowledge_point_id,
                )
            )

            path_id = f"exam_{q.topic.lower().replace(' ', '_')}"
            try:
                progress = learning_store.load(path_id)
                if progress is None:
                    progress = LearningProgress(
                        book_id=path_id,
                        user_id=user_id,
                        status="active",
                    )
                attempt = QuizAttempt(
                    question_id=q.id,
                    knowledge_point_id=q.knowledge_point_id,
                    module_id="exam",
                    is_correct=is_correct,
                    user_answer=sel,
                    error_type=ErrorType.UNDERSTANDING_DEVIATION if not is_correct else None,
                )
                self.learning_service.record_quiz_attempt(progress, attempt)
                learning_store.save(progress)
            except Exception as e:
                pass

        percentage = round((score / total) * 100.0, 1) if total > 0 else 0.0
        result = ExamResult(
            exam_id=exam_id,
            score=score,
            total=total,
            percentage=percentage,
            time_spent_seconds=submission.time_spent_seconds,
            results=results,
            topic_breakdown=topic_breakdown,
        )

        attempt_path = self.attempts_dir / f"{result.attempt_id}.json"
        attempt_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result

    def get_attempt(self, attempt_id: str) -> Optional[ExamResult]:
        attempt_path = self.attempts_dir / f"{attempt_id}.json"
        if not attempt_path.exists():
            return None
        data = json.loads(attempt_path.read_text(encoding="utf-8"))
        return ExamResult.model_validate(data)
