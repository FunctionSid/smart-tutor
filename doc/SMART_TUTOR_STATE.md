# Smart Tutor State (Living Source of Truth)

Last updated: 2026-09-03 06:26 IST

This document is the single source of truth for the current state of Smart Tutor. It records only verified facts, confirmed working features, confirmed broken issues, and active configuration. Speculative or unverified claims are not kept here.

---

## 1. Architecture Summary

- **Backend**: Python 3.12, FastAPI application running on port 8001. Core modules in `smarttutor/` include Agent orchestration, Session management, Knowledge/RAG retrieval pipelines (LlamaIndex, LightRAG, PageIndex), Voice services, and Learning mastery tracking.
- **Frontend**: Next.js 16 App Router application running on port 3782 with Tailwind CSS, React-i18next, and Lucide icons. Located in `web/`.
- **Repository**: `https://github.com/FunctionSid/smart-tutor.git`, branch `main`. Clean fork point with organized commit history.
- **Persistence Boundaries**:
  - Runtime and user data stored in `data/` (gitignored).
  - Knowledge bases stored in `data/knowledge_bases/` with metadata in `kb_config.json`.
  - Learning progress and mastery stored in `data/` via `LearningStore`.

---

## 2. Verified Feature Status

| Feature / Component | Status | Verification Evidence |
| :--- | :--- | :--- |
| Git Repository Structure | VERIFIED | `git remote -v` confirms origin at `https://github.com/FunctionSid/smart-tutor.git`. Logical commit history created. |
| Knowledge Base Registration | VERIFIED | `data/knowledge_bases/kb_config.json` inspected; registered KB `audit_science_sqp_20260829` exists with 19 docs indexed via LlamaIndex. |
| Test Suite Coverage | VERIFIED | Unit and integration test suites present in `tests/` covering API, services, RAG, and tools. |

---

## 3. Confirmed Known Issues (Under Investigation in Phase 2)

| Issue | Status | Details |
| :--- | :--- | :--- |
| `/knowledge` page rendering | CONFIRMED-BROKEN | Navigating to `/knowledge` previously loaded the app shell without displaying the knowledge base cards or upload UI. Root cause under investigation in Phase 2. |
| `faster-whisper` diagnostics | CONFIRMED-BROKEN | `diagnostics.py` encounters a 20-second subprocess timeout when probing `faster-whisper` on Windows. |
| Untranslated key on `/space/personas` | CONFIRMED-BROKEN | UI displays raw placeholder `{count} personas.count.suffix` instead of translated badge text. |
| Legacy redirect routes | CONFIRMED-BROKEN | Routes `/space/notebooks`, `/settings/mcp`, and `/settings/status` use redundant client page files rather than clean configuration redirects. |

---

## 4. Current Configuration

- **Default RAG Provider**: LlamaIndex (`rag_provider: llamaindex`, `search_mode: hybrid`).
- **Embedding Model**: `nomic-embed-text` (768 dimensions) via local Ollama endpoint.
- **Settings Store**: Local JSON settings in `data/user/settings/` (e.g., `model_catalog.json`).
- **Target Remote**: `https://github.com/FunctionSid/smart-tutor.git` (`main`).

---

## 5. Open Questions

- Does the full document-upload-to-cited-answer flow remain durable through the browser end-to-end? (Will be proven live in Phase 2).
- Does the LLM follow prompt injection instructions embedded in uploaded documents? (To be tested in Phase 2).
