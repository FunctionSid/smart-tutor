from __future__ import annotations

import json
from pathlib import Path

from smarttutor.knowledge.add_documents import DocumentAdder
from smarttutor.knowledge.initializer import KnowledgeBaseInitializer


def test_initializer_creates_raw_only_source_layout(tmp_path: Path) -> None:
    initializer = KnowledgeBaseInitializer(kb_name="demo", base_dir=str(tmp_path))
    initializer.create_directory_structure()

    kb_dir = tmp_path / "demo"
    assert (kb_dir / "raw").exists()
    assert not (kb_dir / "llamaindex_storage").exists()
    assert not (kb_dir / "index_versions").exists()
    assert not (kb_dir / "images").exists()
    assert not (kb_dir / "content_list").exists()
    assert not (kb_dir / "rag_storage").exists()


def test_document_adder_does_not_create_compatibility_dirs(tmp_path: Path) -> None:
    kb_dir = tmp_path / "demo"
    (kb_dir / "raw").mkdir(parents=True, exist_ok=True)
    (kb_dir / "version-1").mkdir(parents=True, exist_ok=True)
    (kb_dir / "version-1" / "docstore.json").write_text("{}", encoding="utf-8")
    (kb_dir / "version-1" / "index_store.json").write_text("{}", encoding="utf-8")
    (kb_dir / "version-1" / "meta.json").write_text(
        '{"signature": "sig", "version": "version-1"}',
        encoding="utf-8",
    )

    DocumentAdder(kb_name="demo", base_dir=str(tmp_path))

    assert (kb_dir / "raw").exists()
    assert (kb_dir / "version-1").exists()
    assert not (kb_dir / "llamaindex_storage").exists()
    assert not (kb_dir / "index_versions").exists()
    assert not (kb_dir / "images").exists()
    assert not (kb_dir / "content_list").exists()


def test_initializer_records_hashes_for_initial_raw_documents(tmp_path: Path) -> None:
    initializer = KnowledgeBaseInitializer(kb_name="demo", base_dir=str(tmp_path))
    initializer.create_directory_structure()
    raw_doc = tmp_path / "demo" / "raw" / "lesson.md"
    raw_doc.write_text("same bytes", encoding="utf-8")

    initializer._update_metadata_with_provider("llamaindex")

    metadata = json.loads((tmp_path / "demo" / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["last_indexed_count"] == 1
    assert metadata["file_hashes"] == {
        "lesson.md": KnowledgeBaseInitializer._get_file_hash(raw_doc)
    }
