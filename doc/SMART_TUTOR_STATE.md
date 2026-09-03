# Smart Tutor State (Living Source of Truth)

Last updated: 2026-09-03 09:48 IST

This document is the single source of truth for the current state of Smart Tutor. It records only verified facts, confirmed working features, confirmed broken issues, and active configuration. Speculative or unverified claims are not kept here.

---

## 1. Architecture Summary

- **Backend**: Python 3.12, FastAPI application running on port 8001. Core modules in `smarttutor/` include Agent orchestration, Session management, Knowledge/RAG retrieval pipelines (LlamaIndex, LightRAG, PageIndex), Voice services, Exam autonomous generation, and Learning mastery tracking.
- **Frontend**: Next.js 16 App Router application running on port 3782 with Tailwind CSS, React-i18next, and Lucide icons. Located in `web/`.
- **Repository**: `https://github.com/FunctionSid/smart-tutor.git`, branch `main`. Clean fork point with organized commit history.
- **Persistence Boundaries**:
  - Runtime and user data stored in `data/` (gitignored).
  - Knowledge bases stored in `data/knowledge_bases/` with metadata in `kb_config.json`.
  - Learning progress and mastery stored in `data/` via `LearningStore`.
  - Exams and attempts stored in `data/user/exams/`.

---

## 2. Verified Feature Status

| Feature / Component | Status | Verification Evidence |
| :--- | :--- | :--- |
| Settings Tabbed UI | VERIFIED | Restructured `/settings` into accessible Student and Advanced tabs using `role="tablist"`, `role="tab"`, and `role="tabpanel"`. Verified full keyboard navigation with Arrow keys, proper ARIA attributes, and visible focus rings in Microsoft Edge. |
| Student Settings Panel | VERIFIED | Default tab provides Theme, Interface Language, Active Chat/Tutor Model, Speech-to-Text, Text-to-Speech, Voice Autoplay toggle, Memory Privacy/Clear controls, and Attachment preferences. |
| Image & Video Gen Removal | VERIFIED | Completely removed Image and Video generation: deleted `/settings/image` and `/settings/video` routes, removed `imagegen` and `videogen` from `ServiceName` and frontend catalog types, stopped backend catalog loading in `model_catalog.py`, unregistered builtin tools with zero tool drift verified via `validate_tool_consistency()`. |
| Memory System Integrity | VERIFIED | Memory system remains active and untouched. Verified `/api/v1/memory/overview` returns live L2 and L3 layers; chat trace clear control connected to `DELETE /api/v1/memory/trace/chat`. |
| Exam Mode (Autonomous MCQ) | VERIFIED | Autonomous exam generation graph implemented with strict validation guardrails (single correct answer, no all/none of the above, verbatim grounded citation). Verified with 9 passing unit tests in `tests/exam/` and accessible runner UI in Microsoft Edge. |
| Learning Mastery Integration | VERIFIED | Exam grading feeds into `LearningService.record_quiz_attempt`, verified creation of active `ErrorRecord` on wrong answers and subsequent graduation upon correct retry. |
| Live Browser RAG Pipeline | VERIFIED | End-to-end browser test uploaded `audit_physics_sample.pdf`, indexed via LlamaIndex + Ollama `nomic-embed-text`, bound to chat session, and answered factual and cross-referencing questions with citations. |
| Prompt Injection Resistance | VERIFIED | Model ignored embedded override instruction in indexed document and answered with grounded facts while citing the source PDF. |
| Voice Diagnostics (`faster-whisper`) | VERIFIED | `faster-whisper` v1.2.1 verified working with 45s probe timeout to eliminate Windows cold-start DLL loading timeouts. |

---

## 3. Confirmed Known Issues

| Issue | Status | Details |
| :--- | :--- | :--- |
| None currently unresolved | RESOLVED | Verification gaps closed, Exam mode implemented, accessible Settings tabs built, and media generation cleanly removed. |

---

## 4. Current Configuration

- **Default RAG Provider**: LlamaIndex (`rag_provider: llamaindex`, `search_mode: hybrid`).
- **Embedding Model**: `nomic-embed-text` (768 dimensions) via local Ollama endpoint (`http://localhost:11434/api/embed`).
- **Active LLM**: `gpt-4.1` via OpenAI-compatible endpoint.
- **Default Settings Tab**: Student Settings.
- **Media Generation**: Disabled and removed (Text + Voice tutor only).
- **Target Remote**: `https://github.com/FunctionSid/smart-tutor.git` (`main`).
