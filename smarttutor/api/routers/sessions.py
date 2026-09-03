"""
Unified session history API.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from smarttutor.learning import policy as learning_policy
from smarttutor.learning.grading import classify_error
from smarttutor.learning.models import (
    KnowledgePoint,
    KnowledgeType,
    LearningModule,
    QuizAttempt,
    RetryAttempt,
)
from smarttutor.learning.service import LearningService
from smarttutor.learning.storage import LearningStore
from smarttutor.services.session import get_session_store, get_sqlite_session_store
from smarttutor.services.storage.attachment_store import get_attachment_store

logger = logging.getLogger(__name__)

router = APIRouter()


class SessionRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


class BranchSelectionRequest(BaseModel):
    """Edit-branch picker state: `{parent_message_id: chosen_child_id}`.

    Stored inside the session preferences blob so it survives reloads
    without a dedicated column.
    """

    selected_branches: dict[str, int] = Field(default_factory=dict)


class QuizResultItem(BaseModel):
    question_id: str = ""
    question: str = Field(..., min_length=1)
    question_type: str = ""
    options: dict[str, str] | None = None
    user_answer: str = ""
    correct_answer: str = ""
    explanation: str | None = ""
    difficulty: str | None = ""
    concentration: str | None = ""
    knowledge_context: str | None = ""
    is_correct: bool

    @field_validator("options", mode="before")
    @classmethod
    def _coerce_options(cls, v):
        return v if isinstance(v, dict) else {}

    @field_validator("explanation", "difficulty", "concentration", "knowledge_context", mode="before")
    @classmethod
    def _coerce_str(cls, v):
        return v if isinstance(v, str) else ""


class QuizResultsRequest(BaseModel):
    answers: list[QuizResultItem] = Field(default_factory=list)
    turn_id: str = ""


def _format_quiz_results_message(answers: list[QuizResultItem]) -> str:
    total = len(answers)
    correct = sum(1 for item in answers if item.is_correct)
    score_pct = round((correct / total) * 100) if total else 0
    lines = ["[Quiz Performance]"]
    for idx, item in enumerate(answers, 1):
        question = item.question.strip().replace("\n", " ")
        user_answer = (item.user_answer or "").strip() or "(blank)"
        status = "Correct" if item.is_correct else "Incorrect"
        suffix = f" ({status})"
        if not item.is_correct and (item.correct_answer or "").strip():
            suffix = f" ({status}, correct: {(item.correct_answer or '').strip()})"
        qid = f"[{item.question_id}] " if item.question_id else ""
        lines.append(f"{idx}. {qid}Q: {question} -> Answered: {user_answer}{suffix}")
    lines.append(f"Score: {correct}/{total} ({score_pct}%)")
    return "\n".join(lines)


_SAFE_ID_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")


def _safe_learning_id(prefix: str, value: str, *, max_len: int = 96) -> str:
    clean = _SAFE_ID_CHARS.sub("_", str(value or "")).strip("._-")
    digest = hashlib.sha1(str(value or "").encode("utf-8")).hexdigest()[:12]
    if not clean:
        clean = digest
    clean = clean[: max(1, max_len - len(prefix) - 13)].strip("._-") or digest
    return f"{prefix}{clean}_{digest}"


def _question_type_to_knowledge_type(question_type: str) -> KnowledgeType:
    normalized = str(question_type or "").strip().lower()
    if normalized == "coding":
        return KnowledgeType.PROCEDURE
    if normalized in {"written", "short_answer"}:
        return KnowledgeType.CONCEPT
    return KnowledgeType.MEMORY


def _topic_label(item: QuizResultItem) -> str:
    for candidate in (item.concentration, item.knowledge_context):
        text = str(candidate or "").strip()
        if text:
            return text[:120]
    question = " ".join(item.question.split())
    if question:
        return question[:120]
    return str(item.question_type or "Quiz objective")


def _ensure_quiz_module(
    modules: list[LearningModule],
    *,
    module_id: str,
    module_name: str,
) -> LearningModule:
    for module in modules:
        if module.id == module_id:
            if not module.name:
                module.name = module_name
            return module
    module = LearningModule(
        id=module_id,
        name=module_name,
        order=len(modules),
        pass_threshold=0.9,
        knowledge_points=[],
    )
    modules.append(module)
    return module


def _ensure_knowledge_point(
    module: LearningModule,
    *,
    item: QuizResultItem,
) -> KnowledgePoint:
    topic = _topic_label(item)
    kp_id = _safe_learning_id("quiz_kp_", topic.lower(), max_len=72)
    existing = next((kp for kp in module.knowledge_points if kp.id == kp_id), None)
    kp_type = _question_type_to_knowledge_type(item.question_type)
    if existing is not None:
        return existing
    kp = KnowledgePoint(id=kp_id, name=topic, type=kp_type, module_id=module.id)
    module.knowledge_points.append(kp)
    return kp


def _graduate_recovered_topic_errors(
    progress,
    *,
    knowledge_point_id: str,
    module_id: str,
    mastery: float,
    threshold: float,
) -> int:
    if mastery < threshold:
        return 0
    recovered = 0
    for record in progress.error_records:
        if (
            record.knowledge_point_id == knowledge_point_id
            and record.module_id == module_id
            and record.status in ("active", "retrying")
        ):
            record.retry_history.append(
                RetryAttempt(
                    timestamp=time.time(),
                    is_correct=True,
                    attempt_number=len(record.retry_history) + 1,
                )
            )
            record.status = "graduated"
            recovered += 1
    return recovered


def _record_quiz_learning_progress(
    *,
    session_id: str,
    session_title: str,
    answers: list[QuizResultItem],
    turn_id: str,
) -> dict[str, Any]:
    path_id = _safe_learning_id("session_quiz_", session_id)
    module_id = "quiz_assessment"
    module_name = f"Quiz Assessment: {session_title or session_id}"
    service = LearningService()

    def mutate(tx):
        progress = tx.progress
        module = _ensure_quiz_module(progress.modules, module_id=module_id, module_name=module_name)
        progress.current_module_id = module.id
        progress.knowledge_types.update(
            {kp.id: kp.type for existing in progress.modules for kp in existing.knowledge_points}
        )

        correct = 0
        recovered = 0
        touched_kps: set[str] = set()
        for index, item in enumerate(answers, 1):
            kp = _ensure_knowledge_point(module, item=item)
            progress.knowledge_types[kp.id] = kp.type
            question_id = (
                item.question_id.strip()
                if item.question_id.strip()
                else _safe_learning_id("question_", f"{item.question}:{index}", max_len=64)
            )
            attempt = QuizAttempt(
                question_id=question_id,
                knowledge_point_id=kp.id,
                module_id=module.id,
                is_correct=item.is_correct,
                user_answer=item.user_answer,
                error_type=None if item.is_correct else classify_error(item.user_answer),
            )
            service.record_quiz_attempt(progress, attempt)
            mastery = service.calculate_mastery(progress, kp.id)
            service.update_mastery(progress, kp.id, mastery)
            threshold = learning_policy.gate_threshold(kp.type)
            if item.is_correct:
                correct += 1
                recovered += _graduate_recovered_topic_errors(
                    progress,
                    knowledge_point_id=kp.id,
                    module_id=module.id,
                    mastery=mastery,
                    threshold=threshold,
                )
            touched_kps.add(kp.id)

        total = len(answers)
        active_errors = sum(
            1
            for record in progress.error_records
            if record.module_id == module.id and record.status in ("active", "retrying", "review")
        )
        tx.emit(
            "assessment.quiz_recorded",
            {
                "session_id": session_id,
                "turn_id": turn_id,
                "answer_count": total,
                "correct_count": correct,
                "score_pct": round((correct / total) * 100) if total else 0,
                "knowledge_point_count": len(touched_kps),
                "active_error_count": active_errors,
                "recovered_error_count": recovered,
            },
            session_id=session_id,
            turn_id=turn_id,
        )
        return {
            "progress_path_id": progress.book_id,
            "knowledge_point_count": len(touched_kps),
            "active_error_count": active_errors,
            "recovered_error_count": recovered,
            "correct_count": correct,
            "score_pct": round((correct / total) * 100) if total else 0,
        }

    service.store.bind_session(path_id, session_id, owns_path=True)
    _, result = service.store.mutate(path_id, mutate, create=True)
    return result


@router.get("")
async def list_sessions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    store = get_session_store()
    sessions = await store.list_sessions(limit=limit, offset=offset)
    return {"sessions": sessions}


# Cap (in characters) for a single event payload returned to the UI. RAG
# tools can attach whole KB documents to ``tool_result``/``observation``
# events; the frontend TraceSurface only needs a preview, and the LLM context
# is built from a separate content-only store, so capping here never affects
# model input.
MAX_EVENT_PAYLOAD = 1024 * 1024
_TRUNCATION_NOTICE = "\n\n[... content truncated]"
_TRUNCATABLE_EVENT_TYPES = ("tool_result", "observation")


def _truncate_oversized_events(
    messages: list[dict[str, Any]], limit: int = MAX_EVENT_PAYLOAD
) -> None:
    """Cap oversized ``tool_result``/``observation`` payloads in place.

    The session store already returns each message's events as a parsed
    ``events`` list (see ``SqliteSessionStore._serialize_message``), so we
    mutate that list directly. Only the UI rendering path is affected.
    """

    def _cap(container: dict[str, Any], field: str) -> bool:
        value = container.get(field)
        if isinstance(value, str) and len(value) > limit:
            container[field] = value[:limit] + _TRUNCATION_NOTICE
            return True
        return False

    for msg in messages:
        events = msg.get("events")
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict) or event.get("type") not in _TRUNCATABLE_EVENT_TYPES:
                continue
            truncated = _cap(event, "content")
            tool_metadata = (event.get("metadata") or {}).get("tool_metadata")
            if isinstance(tool_metadata, dict):
                for field in ("content", "answer"):
                    truncated = _cap(tool_metadata, field) or truncated
            if truncated:
                event["_truncated"] = True


@router.get("/{session_id}")
async def get_session(session_id: str):
    store = get_session_store()
    session = await store.get_session_with_messages(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    _truncate_oversized_events(session.get("messages", []))
    return session


@router.patch("/{session_id}")
async def rename_session(session_id: str, payload: SessionRenameRequest):
    store = get_session_store()
    updated = await store.update_session_title(session_id, payload.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    session = await store.get_session(session_id)
    return {"session": session}


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    store = get_session_store()
    list_active_turns = getattr(store, "list_active_turns", None)
    if callable(list_active_turns):
        from smarttutor.services.session import get_turn_runtime_manager

        runtime = get_turn_runtime_manager()
        for turn in await list_active_turns(session_id):
            await runtime.cancel_turn(turn["id"])
    deleted = await store.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        await asyncio.to_thread(LearningStore().detach_session, session_id)
    except Exception:
        logger.exception("failed to detach mastery paths for session %s", session_id)
    try:
        await get_attachment_store().delete_session(session_id)
    except Exception:
        logger.exception("failed to clean up attachments for session %s", session_id)
    return {"deleted": True, "session_id": session_id}


@router.put("/{session_id}/branch-selection")
async def update_branch_selection(session_id: str, payload: BranchSelectionRequest):
    store = get_sqlite_session_store()
    session = await store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    updated = await store.update_session_preferences(
        session_id, {"selected_branches": dict(payload.selected_branches)}
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"selected_branches": payload.selected_branches}


@router.delete("/{session_id}/messages/{message_id}")
async def delete_turn_by_message(session_id: str, message_id: int):
    store = get_sqlite_session_store()
    result = await store.delete_turn_by_message(session_id, message_id)
    if result["was_running"]:
        raise HTTPException(
            status_code=409, detail="Cannot delete a message while its turn is running"
        )
    if not result["deleted"]:
        raise HTTPException(status_code=404, detail="Message not found")
    attachment_store = get_attachment_store()
    for aid in result["attachment_ids"]:
        try:
            await attachment_store.delete_attachment(session_id, aid)
        except Exception:
            logger.exception("failed to delete attachment %s for session %s", aid, session_id)
    return result


@router.post("/{session_id}/quiz-results")
async def record_quiz_results(session_id: str, payload: QuizResultsRequest):
    if not payload.answers:
        raise HTTPException(status_code=400, detail="Quiz results are required")
    store = get_sqlite_session_store()
    session = await store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    content = _format_quiz_results_message(payload.answers)
    await store.add_message(
        session_id=session_id,
        role="user",
        content=content,
        capability="deep_question",
    )
    notebook_count = 0
    try:
        notebook_count = await store.upsert_notebook_entries(
            session_id,
            [{**item.model_dump(), "turn_id": payload.turn_id} for item in payload.answers],
        )
    except Exception:
        logger.warning(
            "Failed to upsert notebook entries for session %s", session_id, exc_info=True
        )
    progress_result: dict[str, Any] = {}
    try:
        progress_result = await asyncio.to_thread(
            _record_quiz_learning_progress,
            session_id=session_id,
            session_title=str(session.get("title") or ""),
            answers=payload.answers,
            turn_id=payload.turn_id,
        )
    except Exception:
        logger.warning(
            "Failed to record quiz results into learning progress for session %s",
            session_id,
            exc_info=True,
        )
    return {
        "recorded": True,
        "session_id": session_id,
        "answer_count": len(payload.answers),
        "notebook_count": notebook_count,
        "progress_updated": bool(progress_result),
        **progress_result,
        "content": content,
    }
