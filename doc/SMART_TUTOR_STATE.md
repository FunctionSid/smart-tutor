# Smart Tutor State (Living Source of Truth)

Last updated: 2026-09-11 IST

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
| Memory Run Model/Status Truthfulness | VERIFIED | Memory update/audit/dedup runs now reject invalid explicit `{profile_id, model_id}` selections instead of silently falling back to the default model. Valid explicit selections emit a `model_selected` run event with the resolved provider/model, total LLM failure ends the run as an error, and the Memory Run UI renders selected-model, no-new-input, no-doc, and no-change outcomes. Verified by focused memory-mode tests and existing memory/API/session tests. |
| Learning Activity Memory Bridge | PARTIALLY VERIFIED | The existing `quiz` memory surface now reads authoritative learning evidence from question/notebook quiz rows, `LearningStore` mastery/progress summaries, and saved exam attempt results. Verified with disposable LearningStore/exam fixtures and a mocked L1 -> L2 -> L3 chain. Real user L2/L3 docs are still only built when a Memory Run is intentionally executed. |
| Exam Mode (Autonomous MCQ) | VERIFIED | Autonomous exam generation graph implemented with strict validation guardrails (single correct answer, 4 options, no all/none of the above, verbatim grounded citation). Verified with live KB generation from `physics_optics_kb_1788397480898`, 9 passing unit tests in `tests/exam/`, and end-to-end browser execution in Microsoft Edge (`web/scripts/test_exam_e2e_browser.mjs`). |
| Exam Learning Integration | VERIFIED | Exam grading feeds directly into `LearningService.record_quiz_attempt`. Verified through direct `LearningStore` queries that mistakes create `ErrorRecord` (status: active), and subsequent correct answers transition the error record to graduated. Verified both programmatically and via real browser submission. |
| Live Browser RAG Pipeline | VERIFIED | End-to-end browser test uploaded `audit_physics_sample.pdf`, indexed via LlamaIndex + Ollama `nomic-embed-text`, bound to chat session, and answered factual and cross-referencing questions with citations. |
| Prompt Injection Resistance | VERIFIED | Model ignored embedded override instruction in indexed document and answered with grounded facts while citing the source PDF. |
| Voice Diagnostics (`faster-whisper`) | VERIFIED | `faster-whisper` v1.2.1 verified working with 45s probe timeout to eliminate Windows cold-start DLL loading timeouts. |
| Voice Recording and Transcription | VERIFIED | Microsoft Edge browser recording verified with fake microphone WAV input. The recorder posted through `/api/v1/voice/stt`, inserted transcript text into the chat composer, and announced `Transcription complete.` through the live region. |
| Local MCP Server & Tools | VERIFIED | Local MCP server implemented in `mcp_server/server.py` and launcher `start-mcp.bat`. Provides `list_study_files`, `read_study_file`, and `calculate`. Smart Tutor MCP manager connects to `http://127.0.0.1:8765/sse` and reports `status: "connected"` via `/api/v1/settings/mcp` and `/api/v1/space/mcp/servers`. Direct tool execution tested and verified. |
| Chat Model Selection (Ollama vs OpenAI) | VERIFIED | `/api/v1/settings/llm-options?refresh_local=true` auto-seeds the missing Ollama LLM profile, discovers 8 chat-capable local Ollama models, keeps OpenAI `gpt-4.1` as the active default, and excludes embedding-only `nomic-embed-text`. Microsoft Edge verified initial chat selector loading requests local refresh and can select `qwen3:4b` under `Local · Ollama`. |
| Model Discovery Cache | VERIFIED | Provider model discovery now uses a process-local TTL cache keyed by provider, base URL, and a SHA-256 credential fingerprint instead of raw secrets. Manual sync can force refresh with `force_refresh=true`; offline providers use per-provider failure backoff and keep stale cached models available when possible. Verified by focused cache tests, settings-router tests, LLM options node tests, TypeScript, targeted ESLint, and `git diff --check`. |
| Krutrim Cloud Model Selection | VERIFIED WITH LIMITATIONS | Smart Tutor detects `KRUTRIM_API_KEY` or `KRUTRIM_CLOUD_API_KEY` from the Windows/process environment without storing the secret in `model_catalog.json`. Provider aliases for `kutrim` and `krutrim` resolve to the Krutrim OpenAI-compatible adapter at `https://cloud.olakrutrim.com/v1`. Live `/v1/models` discovery populated the Krutrim Cloud profile with 10 selectable models: `gpt-oss-20b`, `gpt-oss-120b`, `gemma-4-E4B-it`, `gemma-4-31b-it`, `gemma-4-26B-A4B-it`, `Qwen3.5-9B`, `Qwen3.6-27B`, `Qwen3.6-35B-A3B`, `gpt-oss-120b-at`, and `GLM-5.3-Flash`. A live Smart Tutor runtime smoke test using `gpt-oss-20b` returned `SmartTutor Krutrim OK`, and a live OpenAI-style tool-call probe returned the expected tool call for a RAG-style path. |
| Exam Model Selection | VERIFIED | Exam generation modal now uses the shared LLM selector and submits the selected `{profile_id, model_id}` to `/api/v1/exam/generate`. Backend exam generation resolves the same request-scoped LLM config as chat. Microsoft Edge payload verification confirmed chat and exam send identical selected Ollama IDs. |
| Chat Streaming Screen Reader Announcements | VERIFIED | Streaming assistant text is normal `role="article"` content instead of an `aria-live` region. A dedicated hidden `role="status"` announces only `Smart Tutor is generating a response.` and `Response complete.`. The visual elapsed timer remains visible but is removed from live regions and hidden from the status accessible name. Qwen `<think>` cards remain visible and keyboard-accessible with `aria-live="off"`. Verified by `npm run test:node` with 597 passing node tests and live Microsoft Edge automation against Ollama `qwen3:4b`; NVDA manual verification was not performed. |
| Hands-Free Voice Mode | VERIFIED WITH LIMITATIONS | Additive chat-composer mode starts OFF by default and uses an explicit `OFF -> WAKE_WAITING -> WAKE_DETECTED -> CAPTURING -> TRANSCRIBING -> THINKING -> SPEAKING -> WAKE_WAITING` state machine. Wake word is locked to `Hey Jarvis`; backend verifies/scans the installed OpenWakeWord `hey_jarvis` model with 16 kHz PCM. Captured utterances use the existing `/api/v1/voice/stt` facade, preserving the normal Smart Tutor session/model-selection/RAG path. Streaming assistant text is converted to speech-friendly chunks, strips Qwen `<think>`/Markdown before `/api/v1/voice/tts`, and invalidates in-flight TTS on interruption. Barge-in is always on: Hey Jarvis is immediate, ordinary speech requires sustained local RMS speech activity. Listening is focus-only via browser focus/visibility checks. `Ctrl+H` toggles Hands-Free on/off while Smart Tutor is focused; `Ctrl+R` starts/stops manual recording and prevents browser reload. Space/Enter no longer retrigger Hands-Free after clicking the control because the control blurs itself after activation. If Hands-Free was saved enabled, the control starts wake listening again when the focused Smart Tutor page mounts. Windows SAPI is exposed as a local TTS provider when PowerShell/System.Speech is available, with dynamic voice discovery and rate/volume pass-through. Verified by 610 node tests, targeted ESLint, focused Python tests, live OpenWakeWord wake probe through the configured global STT Python, live `/api/v1/voice/stt` silence probe, live `/api/v1/voice/tts` audio response, and Smart Tutor smoke completion. |
| BAT Startup Flow | VERIFIED | `start-smart-tutor.bat` starts Smart Tutor from `D:\project\deep-tutor`, checks Python/Node/npm, delegates backend/frontend lifecycle to the launcher, waits for readiness before opening the browser, and opens the resolved frontend URL instead of blindly opening a hard-coded page early. Verified frontend URL is `http://localhost:3782`; backend URL is `http://127.0.0.1:8001`. |
| Health Smoke Suite | VERIFIED | `scripts/smoke_smart_tutor.py` checks frontend `/`, `/home`, backend `/`, system status, system diagnostics, knowledge list, exam list, LLM options, and the wake probe. Live run after the latest startup and voice fixes returned `9 passed, 0 skipped, 0 failed`. |
| System Diagnostics Endpoint | VERIFIED | `GET /api/v1/system/diagnostics` is admin-gated/read-only and reports current provider-pool and LlamaIndex index-cache diagnostics for stability troubleshooting. |
| Windows Frontend Tooling | VERIFIED WITH WARNINGS | `npm run lint` now runs through the Windows-safe wrapper and exits successfully. Latest verification: lint passed with 0 errors and 129 existing warnings; `npm run build` passed; `npm run test:node` passed with 610 tests. |
| Frontend Link/Keyboard Audit | VERIFIED | Microsoft Edge Playwright crawl on 2026-09-10 visited 39 internal frontend routes/links from `http://localhost:3782`. Follow-up accessibility cleanup added H1s to `/whisper`, `/memory/l1`, `/memory/l2`, and `/memory/l3`, and explicit accessible names to the audited Settings controls. Edge verification confirmed `/whisper`, `/memory/l1`, `/memory/l2`, `/memory/l3`, `/settings`, `/settings/stt`, `/settings/tts`, `/settings/mcp`, `/settings/network`, `/exam`, and `/knowledge` return HTTP 200, expose H1s, have no nameless visible controls in the checked routes, and log no browser console errors. Settings tab keyboard navigation passed: ArrowRight moved from Student Settings to Advanced Settings. |

---

## 3. Confirmed Known Issues

| Issue | Status | Details |
| :--- | :--- | :--- |
| Hands-Free acoustic/manual verification | OPEN | Backend wake/STT/TTS probes passed live, and the browser focus/keyboard logic is covered by tests, but no real spoken "Hey Jarvis" microphone test, full browser microphone automation test, or NVDA manual verification was performed. Ordinary speech barge-in uses browser RMS activity with echo cancellation/noise suppression constraints requested from `getUserMedia`; dedicated `webrtcvad`/Silero browser-side VAD is not implemented. |
| Krutrim per-model behavior | OPEN | Krutrim Cloud model discovery, selection, runtime routing, and `gpt-oss-20b` tool calling were verified. Every discovered Krutrim model is selectable through Smart Tutor, but each individual model was not separately tested for chat quality, streaming behavior, and OpenAI-compatible tool-calling. Provider-side differences may affect RAG tool behavior on specific models. |
| Existing frontend lint warnings | OPEN | `npm run lint` now completes successfully, but it still reports 129 existing warnings, mostly from current UI text/i18n and image lint rules. These are warnings, not current startup blockers. |
| Empty L2/L3 memory docs | OPEN | L1 workspace snapshot and trace APIs are healthy, including learning/exam evidence on the `quiz` surface, but this local workspace still has no useful L2/L3 markdown facts unless a user intentionally runs memory consolidation. The Run UI now reports no-op/error states clearly, but it does not automatically build memory over real data without user action. |
| Memory picker slot alignment | OPEN | Chat backend accepts `recent`, `profile`, `scope`, `preferences`, and legacy `summary` memory references, while the frontend picker currently exposes fewer labels and injects full L3 concat once any memory ref is selected. |
| Frontend page heading gaps | RESOLVED | `/whisper`, `/memory/l1`, `/memory/l2`, and `/memory/l3` now expose H1s. Verified with Microsoft Edge route/accessibility script on 2026-09-10. |
| Settings control accessible names | RESOLVED | Student auto-play switch, Hands-Free switch, wake-word input, capability enable switch, memory switches, and the embedding "Send dimensions" checkbox now have explicit accessible names. Verified with Microsoft Edge route/accessibility script on 2026-09-10. |
| Playwright default browser install | OPEN | `npm run audit` currently fails before reaching the app because Playwright's default Chromium executable is missing from `C:\Users\Sourabh\AppData\Local\ms-playwright`. The same audit approach works with the installed Microsoft Edge channel. |
| Optional local MCP server | OPEN / CONFIGURATION | `/space/mcp` and `/settings/mcp` load, but the audit run logged `MCP server 'local_tutoring' failed to connect` because `start-mcp.bat` was not running. This is expected unless the optional local MCP server is started separately. |

---

## 4. Current Configuration

- **Default RAG Provider**: LlamaIndex (`rag_provider: llamaindex`, `search_mode: hybrid`).
- **Embedding Model**: `nomic-embed-text` (768 dimensions) via local Ollama endpoint (`http://localhost:11434/api/embed`).
- **Active LLM**: `gpt-4.1` via OpenAI-compatible endpoint.
- **Selectable Local LLMs**: Ollama chat-capable models are discovered on local refresh from `http://localhost:11434/v1`; embedding-only Ollama tags are excluded from LLM selection.
- **Selectable Krutrim Cloud LLMs**: Krutrim models are discovered from `https://cloud.olakrutrim.com/v1` when a process environment key is present. Supported environment variable names are `KRUTRIM_API_KEY` and `KRUTRIM_CLOUD_API_KEY`; the catalog profile intentionally keeps `api_key` blank so the secret stays in the Windows/process environment.
- **Model Discovery Cache**: TTL is 300 seconds; initial failure backoff is 60 seconds; maximum failure backoff is 900 seconds. Cache keys include provider, normalized base URL, and a non-secret credential fingerprint.
- **Hands-Free Wake Word**: `Hey Jarvis` only, backed by the installed OpenWakeWord `hey_jarvis_v0.1`/`hey_jarvis` model.
- **Hands-Free Voice Path**: Browser focus-only microphone loop detects wake word locally, captures one utterance, sends it through existing STT, submits text into the active chat session with the selected model and selected RAG/knowledge context, then streams speech-ready answer chunks through existing TTS. `Ctrl+H` toggles Hands-Free, and `Ctrl+R` toggles manual recording while Smart Tutor is focused. Backend status on 2026-09-10: Hey Jarvis probe loadable, STT endpoint responsive, and TTS endpoint returns playable audio bytes.
- **Windows SAPI**: Exposed as `windows_speech` / `windows_system_speech` when Windows PowerShell/System.Speech is available. Installed SAPI voices are discovered dynamically; no specific Microsoft voice is hard-coded.
- **Default Settings Tab**: Student Settings.
- **Media Generation**: Disabled and removed (Text + Voice tutor only).
- **Target Remote**: `https://github.com/FunctionSid/smart-tutor.git` (`main`).

---

## 5. Latest Verification Snapshot

2026-09-10 local verification:

- `start-smart-tutor.bat` starts backend and frontend, waits for readiness, and opens `http://localhost:3782` only after the frontend is reachable.
- Frontend live URLs verified: `/` and `/home` returned HTTP 200.
- Backend live URLs verified: `/`, `/api/v1/system/status`, `/api/v1/system/diagnostics`, knowledge list, exam list, LLM options, and wake probe.
- `scripts/smoke_smart_tutor.py`: 9 passed, 0 skipped, 0 failed.
- Microsoft Edge frontend link/keyboard crawl: 39 internal routes visited; visible app links resolved; Settings tab keyboard arrow navigation passed.
- Focused route recheck: `/exam`, `/knowledge`, `/settings/network`, and `/settings/mcp` returned HTTP 200 with no console errors when tested directly.
- Frontend accessibility cleanup verification: `/whisper`, `/memory/l1`, `/memory/l2`, `/memory/l3`, `/settings`, `/settings/stt`, `/settings/tts`, `/settings/mcp`, `/settings/network`, `/exam`, and `/knowledge` returned HTTP 200, exposed H1s, had no nameless visible controls in the checked routes, and produced no browser console errors in Microsoft Edge.
- `npm run test:node`: 610 tests passed.
- `npm run build`: passed.
- `npm run lint`: passed with 0 errors and 129 existing warnings.
- `.\.venv\Scripts\python.exe -m pytest tests\services\test_voice.py tests\api\test_voice_routes.py -q`: 38 tests passed.

2026-09-11 local verification:

- `.\.venv\Scripts\python.exe -m pytest tests\services\memory\test_snapshot_adapters.py -q`: 9 tests passed.
- `.\.venv\Scripts\python.exe -m pytest tests\services\memory\test_modes.py -q`: 12 tests passed.
- `.\.venv\Scripts\python.exe -m pytest tests\services\memory tests\api\test_memory_resolver.py tests\services\session\test_turn_runtime.py -q`: 197 tests passed.
- `.\.venv\Scripts\python.exe -m pytest smarttutor\learning\tests tests\exam\test_exam_learning_integration.py tests\api\test_notebook_router.py::test_quiz_results_update_learning_progress -q`: 298 tests passed.
- `.\.venv\Scripts\python.exe -m pytest tests\exam\test_exam_learning_integration.py -q`: 1 test passed.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint -- components/memory/MemoryRunPanel.tsx`: passed with 0 errors and the existing 129 warnings across the wider lint scan.
