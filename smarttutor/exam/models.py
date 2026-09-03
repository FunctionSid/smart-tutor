from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field
import uuid
import time


class Citation(BaseModel):
    source: str
    page: Optional[int] = None
    quote: str


class ExamQuestion(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    topic: str
    question: str
    options: List[str]
    correct_option: Literal["A", "B", "C", "D"]
    explanation: str
    citation: Citation
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    knowledge_point_id: str


class ExamSpec(BaseModel):
    exam_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    title: str
    topic: str
    kb_name: str
    num_questions: int
    time_limit_minutes: Optional[int] = None
    questions: List[ExamQuestion]
    created_at: float = Field(default_factory=time.time)


class QuestionValidation(BaseModel):
    valid: bool
    has_single_correct: bool
    distractors_unambiguous: bool
    no_all_or_none: bool
    citation_grounded: bool
    feedback: str = ""


class ExamSubmission(BaseModel):
    answers: dict[str, str]
    time_spent_seconds: int = 0


class QuestionResult(BaseModel):
    question_id: str
    question: str
    options: List[str]
    selected_option: Optional[str]
    correct_option: str
    is_correct: bool
    explanation: str
    citation: Citation
    topic: str
    knowledge_point_id: str


class ExamResult(BaseModel):
    attempt_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    exam_id: str
    score: int
    total: int
    percentage: float
    time_spent_seconds: int
    results: List[QuestionResult]
    topic_breakdown: dict[str, dict[str, int]]
    submitted_at: float = Field(default_factory=time.time)
