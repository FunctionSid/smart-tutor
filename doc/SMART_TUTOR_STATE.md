# Smart Tutor State (Living Source of Truth)

Last updated: 2026-09-04 14:55 IST

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
| Exam Mode (Autonomous MCQ) | VERIFIED | Autonomous exam generation graph implemented with strict validation guardrails (single correct answer, 4 options, no all/none of the above, verbatim grounded citation). Verified with live KB generation from `physics_optics_kb_1788397480898`, 9 passing unit tests in `tests/exam/`, and end-to-end browser execution in Microsoft Edge (`web/scripts/test_exam_e2e_browser.mjs`). |
| Exam Learning Integration | VERIFIED | Exam grading feeds directly into `LearningService.record_quiz_attempt`. Verified through direct `LearningStore` queries that mistakes create `ErrorRecord` (status: active), and subsequent correct answers transition the error record to graduated. Verified both programmatically and via real browser submission. |
| Live Browser RAG Pipeline | VERIFIED | End-to-end browser test uploaded `audit_physics_sample.pdf`, indexed via LlamaIndex + Ollama `nomic-embed-text`, bound to chat session, and answered factual and cross-referencing questions with citations. |
| Prompt Injection Resistance | VERIFIED | Model ignored embedded override instruction in indexed document and answered with grounded facts while citing the source PDF. |
| Voice Diagnostics (`faster-whisper`) | VERIFIED | `faster-whisper` v1.2.1 verified working with 45s probe timeout to eliminate Windows cold-start DLL loading timeouts. |
| Voice Recording and Transcription | VERIFIED | Microsoft Edge browser recording verified with fake microphone WAV input. The recorder posted through `/api/v1/voice/stt`, inserted transcript text into the chat composer, and announced `Transcription complete.` through the live region. |
| Local MCP Server & Tools | VERIFIED | Local MCP server implemented in `mcp_server/server.py` and launcher `start-mcp.bat`. Provides `list_study_files`, `read_study_file`, and `calculate`. Smart Tutor MCP manager connects to `http://127.0.0.1:8765/sse` and reports `status: "connected"` via `/api/v1/settings/mcp` and `/api/v1/space/mcp/servers`. Direct tool execution tested and verified. |
| Chat Model Selection (Ollama vs OpenAI) | VERIFIED | `/api/v1/settings/llm-options?refresh_local=true` auto-seeds the missing Ollama LLM profile, discovers 8 chat-capable local Ollama models, keeps OpenAI `gpt-4.1` as the active default, and excludes embedding-only `nomic-embed-text`. Microsoft Edge verified initial chat selector loading requests local refresh and can select `qwen3:4b` under `Local · Ollama`. |
| Exam Model Selection | VERIFIED | Exam generation modal now uses the shared LLM selector and submits the selected `{profile_id, model_id}` to `/api/v1/exam/generate`. Backend exam generation resolves the same request-scoped LLM config as chat. Microsoft Edge payload verification confirmed chat and exam send identical selected Ollama IDs. |
| Chat Streaming Screen Reader Announcements | VERIFIED | Streaming assistant text is normal `role="article"` content instead of an `aria-live` region. A dedicated hidden `role="status"` announces only `Smart Tutor is generating a response.` and `Response complete.`. The visual elapsed timer remains visible but is removed from live regions and hidden from the status accessible name. Qwen `<think>` cards remain visible and keyboard-accessible with `aria-live="off"`. Verified by `npm run test:node` with 597 passing node tests and live Microsoft Edge automation against Ollama `qwen3:4b`; NVDA manual verification was not performed. |

---

## 3. Confirmed Known Issues

| Issue | Status | Details |
| :--- | :--- | :--- |
| None currently confirmed | RESOLVED | Ollama chat model discovery, exam model routing, and voice recorder transcription were verified on 2026-09-04. |

---

## 4. Current Configuration

- **Default RAG Provider**: LlamaIndex (`rag_provider: llamaindex`, `search_mode: hybrid`).
- **Embedding Model**: `nomic-embed-text` (768 dimensions) via local Ollama endpoint (`http://localhost:11434/api/embed`).
- **Active LLM**: `gpt-4.1` via OpenAI-compatible endpoint.
- **Selectable Local LLMs**: Ollama chat-capable models are discovered on local refresh from `http://localhost:11434/v1`; embedding-only Ollama tags are excluded from LLM selection.
- **Default Settings Tab**: Student Settings.
- **Media Generation**: Disabled and removed (Text + Voice tutor only).
- **Target Remote**: `https://github.com/FunctionSid/smart-tutor.git` (`main`).
