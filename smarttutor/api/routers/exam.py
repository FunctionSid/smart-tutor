from __future__ import annotations

from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from smarttutor.exam.models import ExamResult, ExamSpec, ExamSubmission
from smarttutor.exam.service import ExamService

router = APIRouter(prefix="/exam", tags=["exam"])
_service = ExamService()


class GenerateExamRequest(BaseModel):
    topic: str
    kb_name: str
    num_questions: int = 5
    difficulty: str = "medium"
    time_limit_minutes: Optional[int] = None
    llm_selection: Optional[dict[str, str]] = None


@router.post("/generate", response_model=ExamSpec)
async def generate_exam(req: GenerateExamRequest) -> ExamSpec:
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic must not be empty.")
    if not req.kb_name.strip():
        raise HTTPException(status_code=400, detail="kb_name must not be empty.")
    if req.num_questions < 1 or req.num_questions > 50:
        raise HTTPException(status_code=400, detail="num_questions must be between 1 and 50.")

    exam = await _service.create_exam(
        topic=req.topic,
        kb_name=req.kb_name,
        num_questions=req.num_questions,
        difficulty=req.difficulty,
        time_limit_minutes=req.time_limit_minutes,
        llm_selection=req.llm_selection,
    )
    sanitized = _service.get_exam(exam.exam_id, hide_answers=True)
    if sanitized is None:
        return exam
    return sanitized


@router.get("/list")
async def list_exams() -> List[dict[str, Any]]:
    return _service.list_exams()


@router.get("/{exam_id}", response_model=ExamSpec)
async def get_exam(exam_id: str, reveal: bool = Query(False)) -> ExamSpec:
    exam = _service.get_exam(exam_id, hide_answers=not reveal)
    if exam is None:
        raise HTTPException(status_code=404, detail=f"Exam {exam_id} not found.")
    return exam


@router.post("/{exam_id}/submit", response_model=ExamResult)
async def submit_exam(exam_id: str, submission: ExamSubmission) -> ExamResult:
    try:
        return _service.submit_exam(exam_id, submission)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attempts/{attempt_id}", response_model=ExamResult)
async def get_attempt(attempt_id: str) -> ExamResult:
    attempt = _service.get_attempt(attempt_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail=f"Attempt {attempt_id} not found.")
    return attempt
