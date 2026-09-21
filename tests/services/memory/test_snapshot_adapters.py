"""Snapshot adapter tests — focus on the partner-conversation bridge.

Partner runtimes persist their conversations as JSONL under
``<admin>/partners/<id>/sessions/*.jsonl`` (a store separate from the
chat-history SQLite DB). ``read_partner_entities`` bridges those files
into the ``partner`` memory surface so they consolidate into L2/L3 like
any other surface, tagged with the originating partner.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from smarttutor.services.memory.snapshot import adapters


class _FakePathService:
    def __init__(self, root: Path) -> None:
        self.workspace_root = root

    def get_workspace_dir(self) -> Path:
        return self.workspace_root

    def get_chat_history_db(self) -> Path:
        return self.workspace_root / "chat_history.sqlite3"


def _write_session(sessions_dir: Path, key: str, turns: list[tuple[str, str]]) -> None:
    from smarttutor.partners.helpers import safe_filename

    sessions_dir.mkdir(parents=True, exist_ok=True)
    with (sessions_dir / f"{safe_filename(key).strip('.') or 'default'}.jsonl").open(
        "w", encoding="utf-8"
    ) as fh:
        for i, (role, content) in enumerate(turns):
            fh.write(
                json.dumps(
                    {"role": role, "content": content, "timestamp": f"2026-06-16T10:0{i}:00"},
                    ensure_ascii=False,
                )
                + "\n"
            )


@pytest.fixture
def partner_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Make ``tmp_path`` the admin root and route both path services there."""
    monkeypatch.setattr(adapters, "get_path_service", lambda: _FakePathService(tmp_path))
    import smarttutor.multi_user.paths as mu_paths

    monkeypatch.setattr(mu_paths, "get_admin_path_service", lambda: _FakePathService(tmp_path))
    return tmp_path


def test_partner_sessions_become_tagged_entities(partner_tree: Path) -> None:
    pdir = partner_tree / "partners" / "bot1"
    (pdir).mkdir(parents=True)
    (pdir / "config.yaml").write_text("name: Math Tutor\n", encoding="utf-8")
    _write_session(
        pdir / "sessions",
        "telegram:42",
        [("user", "what is a limit"), ("assistant", "a limit is...")],
    )

    entities = adapters.read_partner_entities()

    assert len(entities) == 1
    ent = entities[0]
    assert ent.id == "bot1:telegram_42"
    # Partner tag lands in both the label and the metadata.
    assert "Math Tutor" in ent.label
    assert ent.metadata["partner_id"] == "bot1"
    assert ent.metadata["partner_name"] == "Math Tutor"
    assert ent.metadata["message_count"] == 2
    assert ent.metadata["archived"] is False
    # Conversation is inlined as role blocks for L2 to chew on.
    assert "### user" in ent.content
    assert "what is a limit" in ent.content


def test_archived_sessions_included_and_flagged(partner_tree: Path) -> None:
    pdir = partner_tree / "partners" / "bot1"
    pdir.mkdir(parents=True)
    _write_session(pdir / "sessions", "web:s1", [("user", "hi"), ("assistant", "hello")])
    _write_session(
        pdir / "sessions",
        "_archived_20260101-000000_web_s1",
        [("user", "old"), ("assistant", "older")],
    )

    entities = adapters.read_partner_entities()

    by_id = {e.id: e for e in entities}
    assert len(by_id) == 2
    archived = next(e for e in entities if e.metadata["archived"])
    assert archived.metadata["session_key"].startswith("_archived_")


def test_empty_sessions_skipped_and_name_falls_back_to_id(partner_tree: Path) -> None:
    pdir = partner_tree / "partners" / "bot2"
    pdir.mkdir(parents=True)
    # whitespace-only content → no usable turns → no entity
    _write_session(pdir / "sessions", "web:empty", [("user", "   "), ("assistant", "")])

    entities = adapters.read_partner_entities()
    assert entities == []


def test_missing_config_uses_dir_id_as_name(partner_tree: Path) -> None:
    pdir = partner_tree / "partners" / "bot3"
    pdir.mkdir(parents=True)
    _write_session(pdir / "sessions", "web:s", [("user", "q"), ("assistant", "a")])

    entities = adapters.read_partner_entities()
    assert len(entities) == 1
    assert entities[0].metadata["partner_name"] == "bot3"


def test_non_admin_scope_sees_no_partners(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A regular user's memory view must not surface admin partner chats."""
    admin_root = tmp_path / "admin"
    user_root = tmp_path / "users" / "u1" / "workspace"
    pdir = admin_root / "partners" / "bot1"
    pdir.mkdir(parents=True)
    _write_session(pdir / "sessions", "web:s", [("user", "q"), ("assistant", "a")])

    monkeypatch.setattr(adapters, "get_path_service", lambda: _FakePathService(user_root))
    import smarttutor.multi_user.paths as mu_paths

    monkeypatch.setattr(mu_paths, "get_admin_path_service", lambda: _FakePathService(admin_root))

    assert adapters.read_partner_entities() == []


def test_non_admin_sees_only_assigned_private_partner_sessions(
    partner_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from smarttutor.multi_user.models import CurrentUser, UserScope
    from smarttutor.multi_user.paths import user_context

    pdir = partner_tree / "partners" / "bot1"
    pdir.mkdir(parents=True)
    _write_session(pdir / "sessions", "admin", [("user", "admin secret")])
    _write_session(pdir / "users" / "u1" / "sessions", "mine", [("user", "my chat")])
    _write_session(pdir / "users" / "u2" / "sessions", "theirs", [("user", "their chat")])

    import smarttutor.multi_user.partner_access as partner_access

    monkeypatch.setattr(
        partner_access,
        "load_grant",
        lambda uid: {"partners": [{"partner_id": "bot1"}]} if uid == "u1" else {},
    )
    root = (partner_tree / "users" / "u1").resolve()
    user = CurrentUser("u1", "alice", "user", UserScope("user", "u1", root))
    with user_context(user):
        entities = adapters.read_partner_entities()

    assert [entity.id for entity in entities] == ["bot1:mine"]
    assert "my chat" in entities[0].content
    assert "admin secret" not in entities[0].content
    assert "their chat" not in entities[0].content


def test_fingerprint_changes_when_conversation_grows(partner_tree: Path) -> None:
    pdir = partner_tree / "partners" / "bot1"
    pdir.mkdir(parents=True)
    _write_session(pdir / "sessions", "web:s", [("user", "q1"), ("assistant", "a1")])
    fp1 = adapters.read_partner_entities()[0].fingerprint

    # Append another exchange → fingerprint must move so refresh detects it.
    _write_session(
        pdir / "sessions",
        "web:s",
        [("user", "q1"), ("assistant", "a1"), ("user", "q2"), ("assistant", "a2")],
    )
    fp2 = adapters.read_partner_entities()[0].fingerprint
    assert fp1 != fp2


def test_quiz_entities_include_learning_store_summary(tmp_path: Path, monkeypatch) -> None:
    from smarttutor.learning.models import (
        ErrorType,
        KnowledgePoint,
        KnowledgeType,
        LearningModule,
        LearningProgress,
        QuizAttempt,
    )
    from smarttutor.learning.service import LearningService
    from smarttutor.learning.storage import LearningStore

    monkeypatch.setattr(adapters, "get_path_service", lambda: _FakePathService(tmp_path))

    kp = KnowledgePoint(
        id="kp_critical_angle",
        name="Critical angle",
        type=KnowledgeType.CONCEPT,
        module_id="optics",
    )
    progress = LearningProgress(
        book_id="exam_optics",
        modules=[LearningModule(id="optics", name="Optics", order=0, knowledge_points=[kp])],
        knowledge_types={kp.id: kp.type},
    )
    service = LearningService()
    for question_id, is_correct in [
        ("q_critical_angle", False),
        ("q_critical_angle", False),
        ("q_critical_angle", True),
        ("q_critical_angle_followup", True),
    ]:
        service.record_quiz_attempt(
            progress,
            QuizAttempt(
                question_id=question_id,
                knowledge_point_id=kp.id,
                module_id="optics",
                is_correct=is_correct,
                user_answer="B" if is_correct else "A",
                error_type=None if is_correct else ErrorType.UNDERSTANDING_DEVIATION,
            ),
        )
    progress.mastery_levels[kp.id] = service.calculate_mastery(progress, kp.id)
    LearningStore(root=tmp_path / "learning").save(progress)

    entities = adapters.read_quiz_entities()

    entity = next(e for e in entities if e.id == "learning:exam_optics")
    assert entity.metadata["source"] == "learning_store"
    assert "Critical angle" in entity.content
    assert "attempts=4" in entity.content
    assert "wrong=2" in entity.content
    assert "recent=WWCC" in entity.content
    assert "mastery=" in entity.content


def test_quiz_entities_include_exam_attempt_summary(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(adapters, "get_path_service", lambda: _FakePathService(tmp_path))
    attempts_dir = tmp_path / "exams" / "attempts"
    attempts_dir.mkdir(parents=True)
    (attempts_dir / "attempt_1.json").write_text(
        json.dumps(
            {
                "attempt_id": "attempt_1",
                "exam_id": "exam_optics",
                "score": 1,
                "total": 2,
                "percentage": 50.0,
                "time_spent_seconds": 90,
                "submitted_at": 1780000000.0,
                "topic_breakdown": {"Optics": {"correct": 1, "total": 2}},
                "results": [
                    {"topic": "Optics", "is_correct": False},
                    {"topic": "Optics", "is_correct": True},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    entities = adapters.read_quiz_entities()

    entity = next(e for e in entities if e.id == "exam:attempt_1")
    assert entity.metadata["source"] == "exam_attempt"
    assert entity.metadata["percentage"] == 50.0
    assert "Score: 1/2 (50.0%)" in entity.content
    assert "Missed topics: {'Optics': 1}" in entity.content
