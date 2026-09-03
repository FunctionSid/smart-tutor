# Smart Tutor Current State And Plan

Audit date: 2026-09-03  
Workspace audited: `D:\project\deep-tutor`  
Requested source docs reviewed: `doc/PROJECT_ARCHITECTURE_AND_CUSTOMIZATION.md`, `doc/SMART_TUTOR_FEATURES.md`, `doc/SMART_TUTOR_STATUS.md`, `doc/SMART_TUTOR_TRANSFORMATION_SPEC.md`, `doc/SMART_TUTOR_VOICE_STT_TTS_REPORT.md`

This report treats the older docs as claims, not truth. Evidence below comes from the current workspace, focused tests, API calls, and a running local app.

## Part A - Current State Audit

### A1. Repo Ground Truth

| Item | Finding | Evidence |
| --- | --- | --- |
| Actual workspace | The live workspace is `D:\project\deep-tutor`. | Command: `Get-Location` returned `D:\project\deep-tutor`. |
| `D:\project\smart-tutor` | No separate checkout exists at that path on this machine. | Command: `Test-Path -LiteralPath 'D:\project\smart-tutor'` returned `False`. |
| Git remote | The repo remote is still upstream DeepTutor. | `git remote -v` returned `https://github.com/HKUDS/DeepTutor.git` for fetch/push. |
| Branch | Current branch is `main`, tracking `origin/main`. | `git status --short --branch` began with `## main...origin/main`. |
| Last commits | Recent committed history is upstream DeepTutor v1.5.16 plus knowledge/RAG changes. | `git log --oneline -30` began with `8515dfdb release: v1.5.16`, followed by MarginNote/Knowledge/RAG commits. |
| Worktree state | The checkout is very dirty: 1,588 status entries. Many `deeptutor/` files are deleted and new `smarttutor/`, `smarttutor_cli/`, `smarttutor_web/`, `doc/`, and packaging files are untracked. | Command: `git status --short | Measure-Object` returned `Count 1588`; first lines showed many modified/deleted files and untracked `smarttutor/`, `smarttutor_cli/`, `smarttutor_web/`. |
| STATUS.md "Files Changed" | The list is directionally real but incomplete/stale relative to the current dirty tree. | `doc/SMART_TUTOR_STATUS.md:396-411` lists a small voice/knowledge file set; `git status` shows 1,588 changed entries across the repo. |
| "Phase 1 docs only" claim | No longer true for this workspace. Real runtime code exists under `smarttutor/`, routes are mounted, the app starts, voice adapters exist, and learning tests pass. | `smarttutor/api/main.py:493` mounts `/api/v1/voice`; `smarttutor/api/routers/sessions.py:415-450` records quiz results; tests below passed. |

### A2. App Startup And Health

I started the app with:

```powershell
.\.venv\Scripts\smarttutor.exe start --dev
```

Observed startup output:

```text
Backend    http://127.0.0.1:8001
Frontend   http://localhost:3782
Workspace  D:\project\deep-tutor
Frontend runtime: source
Starting backend ...
backend  INFO:     Application startup complete.
backend  INFO:     Uvicorn running on http://0.0.0.0:8001
Backend is ready.
Starting frontend ...
frontend ▲ Next.js 16.3.3 (Turbopack)
frontend - Local:         http://localhost:3782
frontend ✓ Ready in 3.7s
Frontend is ready.
Open http://localhost:3782 in your browser.
```

Warnings/errors:

```text
frontend Browserslist: browsers data (caniuse-lite) is 9 months old.
```

Health/API checks:

| Endpoint | Result |
| --- | --- |
| `GET /` | `{"message":"Welcome to Smart Tutor API"}` |
| `GET /api/v1/system/health` | `404 {"detail":"Not Found"}` |
| `GET /api/v1/settings` | `200`; returned UI settings, model catalog, providers, and active voice config |
| `GET /api/v1/settings/options` | `404 {"detail":"Not Found"}` |
| `GET /api/v1/voice/capabilities` | `200`; diagnostic payload returned, but faster-whisper timed out in this run |

### A3. Page-By-Page Smoke Audit

Route tree source: `rg --files web/app`. Browser smoke used the running app at `http://localhost:3782`. This smoke verified route rendering and visible copy, not every button side effect.

| Route | Visible claim / page role | Render verdict | Notes |
| --- | --- | --- | --- |
| `/` | Smart Tutor shell with My Library, Tutor, Practice, Revision, Progress | WORKING | Sidebar IA is Smart Tutor, not old generic SmartTutor. Source: `web/components/sidebar/SidebarShell.tsx:40-67`. |
| `/home` | Tutor/chat: "What would you like to learn?" with quick actions | PARTIALLY WORKING | Renders; full chat send requires provider/key runtime and was not exercised in browser. |
| `/knowledge` | My Library / Knowledge entry | PARTIALLY WORKING | Smoke showed shell only during short wait. Source route exists at `web/app/(utility)/knowledge/page.tsx`. Full upload/index journey NOT VERIFIED in this run. |
| `/notebook` | Notebook entry | PARTIALLY WORKING | Smoke showed shell only during short wait. |
| `/memory` | "Memory" / Progress surface | WORKING | Renders Memory hub, Refresh, links to layers. |
| `/memory/graph` | Memory graph | PARTIALLY WORKING | Renders "Composing memory graph..." during smoke; graph completion not verified. |
| `/memory/l1` | Workspace mirror | WORKING | Renders layer tabs and empty state. |
| `/memory/l2` | Per-surface summaries | WORKING | Renders layer tabs and empty state. |
| `/memory/l3` | Cross-surface knowledge | WORKING | Renders summary/profile/scope controls. |
| `/memory/resolve` | Resolve memory item | PARTIALLY WORKING | Renders "Missing ?id= in URL"; reachable but needs query parameter. |
| `/space` | Study Hub | WORKING | Renders hub cards for chat history/notebooks/etc. |
| `/space/learning` | Revision / spaced review | PARTIALLY WORKING | Renders empty state and "New (in Chat)"; backend progress integration verified by tests, not live browser journey. |
| `/space/questions` | Question Bank / Practice | PARTIALLY WORKING | Renders empty question bank controls; full practice loop not verified. |
| `/space/chat-history` | Chat History | WORKING | Renders empty history and Refresh. |
| `/space/notebooks` | Notebooks | WORKING/PARTIAL | Frontend log showed `GET /space/notebooks 307`, then `GET /notebook 200`; this is a redirect/alias, not an independent page. |
| `/space/personas` | Personas | PARTIALLY WORKING | Renders but showed untranslated `personas.count.suffix`, a visible i18n defect. |
| `/space/skills` | Skills | PARTIALLY WORKING | Renders empty state; import/create side effects not tested. |
| `/space/mcp` | MCP Services | PARTIALLY WORKING | Renders installed/store tabs; connection side effects not tested. |
| `/space/cli-apps` | CLI Apps | PARTIALLY WORKING | Renders installed/store tabs; install side effects not tested. |
| `/agents` | Connected agents | PARTIALLY WORKING | Renders Add agent; actual external-agent workflow not tested. |
| `/settings` | Settings hub | WORKING | Renders; backend `/api/v1/settings` loads. |
| `/settings/appearance` | Appearance/theme/language | PARTIALLY WORKING | Renders controls; persistence not changed in this audit to avoid altering user settings. |
| `/settings/network` | Network/CORS/timeout | PARTIALLY WORKING | Renders; source has GET/PUT network endpoints at `smarttutor/api/routers/settings.py:844-871`. Restart-required behavior not verified. |
| `/settings/models` | Model settings hub | WORKING | Renders model links. |
| `/settings/llm` | AI / Tutor Model | PARTIALLY WORKING | Renders; provider test path exists, live LLM diagnostic not run. |
| `/settings/embedding` | Embedding Model | PARTIALLY WORKING | Renders; embedding diagnostic not run. |
| `/settings/search` | Search provider | PARTIALLY WORKING | Renders; search diagnostic not run. |
| `/settings/tts` | Text-to-Speech | WORKING/PARTIAL | Renders; `POST /api/v1/voice/tts` produced `data/user/voice_audit/current_report_tts.mp3` at 15,552 bytes. |
| `/settings/stt` | Speech-to-Text | PARTIALLY WORKING | Renders; faster-whisper provider is selected but diagnostic timed out in this run. |
| `/settings/image` | Image generation | UI ONLY / PARTIAL | Renders; active imagegen profile is `null` in `/api/v1/settings`. |
| `/settings/video` | Video generation | UI ONLY / PARTIAL | Renders; active videogen profile is `null` in `/api/v1/settings`. |
| `/settings/document-parsing` | Document parsing engines | PARTIALLY WORKING | Renders; source has GET/PUT/test/install/model-download endpoints at `smarttutor/api/routers/settings.py:1063-1286`. |
| `/settings/tools` | User-toggleable tools | PARTIALLY WORKING | Renders loading state in smoke; source has enabled-tools update at `smarttutor/api/routers/settings.py:1586-1593`. |
| `/settings/capabilities` | Capability settings | PARTIALLY WORKING | Renders only shell/loading in smoke. |
| `/settings/memory` | Memory settings | PARTIALLY WORKING | Renders only shell/loading in smoke. |
| `/settings/agents` | Partners & Agents settings | PARTIALLY WORKING | Renders subagent provider links. |
| `/settings/mcp` | MCP Services | WORKING/PARTIAL | Frontend log showed `GET /settings/mcp 307`, then `GET /space/mcp 200`; this is a redirect/alias. |
| `/settings/status` | Status page | WORKING/PARTIAL | Frontend log showed `GET /settings/status 307`, then `GET /settings 200`; this is a redirect/alias, not an independent status page in the running app. |
| `/settings/attachments` | Attachment settings | PARTIALLY WORKING | Renders loading state; source has chat attachment GET/PUT at `smarttutor/api/routers/settings.py:899-938`. |
| `/settings/starters` | Starting points | PARTIALLY WORKING | Renders loading state; source has GET/PUT at `smarttutor/api/routers/settings.py:906-929`. |
| `/book` | AI-authored books | PARTIALLY WORKING | Renders library empty state and New book; generation not tested. |
| `/co-writer` | Markdown drafts/projects | PARTIALLY WORKING | Renders "Loading drafts..."; create/edit not tested. |
| `/partners` | Assigned partners | PARTIALLY WORKING | Renders; no assigned partner action tested. |
| `/partners/new` | Partner creation wizard | PARTIALLY WORKING | Renders wizard; browser side effects not submitted. |
| `/whisper` | Dual-seat supervision | PARTIALLY WORKING | Renders "Connecting..."; room/send workflow not tested. |
| `/playground` | Tools/capabilities playground | WORKING/PARTIAL | Renders overview; individual capability runs not tested. |
| `/profile` | User profile | PARTIALLY WORKING | Renders "Loading..."; profile load completion not verified. |
| `/login` | Auth login | WORKING/PARTIAL | Renders form. Login not tested. |
| `/register` | Auth register | WORKING/PARTIAL | Renders form. Registration not tested. |
| `/admin/users` | User management | WORKING/PARTIAL | Renders Add user/Refresh. Admin mutations not tested. |

Main "pages that talk but do nothing" findings from smoke:

- `/settings/status`, `/settings/mcp`, and `/space/notebooks` are redirect aliases rather than independent pages, despite source files existing in the route tree.
- `/space/personas` has an untranslated visible key, `personas.count.suffix`.
- `/knowledge`, `/notebook`, `/space/notebooks`, `/settings/capabilities`, `/settings/memory`, and several settings subpages showed shell/loading states in the short browser smoke; they need targeted E2E checks before being called working.
- `Image Generation` and `Video Generation` settings render, but `/api/v1/settings` showed no active `imagegen` or `videogen` profile, so those are UI/config surfaces until configured.

### A4. Settings Audit

Settings are real, but not every control was mutation-tested because changing user settings would alter this machine state.

Evidence:

- `GET /api/v1/settings` returned current saved values, including `ui.theme = snow`, `ui.language = en`, active LLM profile, Ollama embedding profile, DuckDuckGo search profile, active `tts-profile-global-edge`, and active `stt-profile-global-faster-whisper`.
- UI settings load/save helpers are implemented in `smarttutor/api/routers/settings.py:430-480`.
- Main settings endpoint is `smarttutor/api/routers/settings.py:736-744`.
- Catalog persistence is exposed at `smarttutor/api/routers/settings.py:838-839`, `smarttutor/api/routers/settings.py:1375-1387`, and `smarttutor/api/routers/settings.py:1387-1409`.
- Diagnostic buttons are wired to real backend runs: frontend starts `/api/v1/settings/tests/{service}/start` and subscribes to `/api/v1/settings/tests/{service}/{run_id}/events` at `web/components/settings/SettingsContext.tsx:1086-1124`; backend routes exist at `smarttutor/api/routers/settings.py:1593-1604`.
- Runtime JSON settings service persists system/auth/integrations/document parsing/RAG slices via `save_*` methods in `smarttutor/services/config/runtime_settings.py:414-556`.

Settings page verdicts:

| Settings area | Loads? | Shows current saved value? | Save persistence verified? | Real diagnostic? | Verdict |
| --- | --- | --- | --- | --- | --- |
| Appearance | Yes | API provides `snow`, `en`; UI showed loading then controls | NOT VERIFIED by mutation | N/A | PARTIAL |
| Network | Yes | API/source expose effective and stored settings | NOT VERIFIED by mutation | N/A | PARTIAL |
| Models hub | Yes | Links render | N/A | N/A | WORKING |
| LLM | Yes | Catalog returned active OpenAI profile | NOT VERIFIED by mutation | Real route exists, not run | PARTIAL |
| Embedding | Yes | Catalog returned active Ollama embedding | NOT VERIFIED by mutation | Real route exists, not run | PARTIAL |
| Search | Yes | Catalog returned DuckDuckGo | NOT VERIFIED by mutation | Real route exists, not run | PARTIAL |
| TTS | Yes | Catalog returned active Edge TTS | TTS endpoint tested, not settings mutation | Real TTS endpoint tested | WORKING/PARTIAL |
| STT | Yes | Catalog returned faster-whisper | NOT VERIFIED by mutation | Capabilities route ran; active faster-whisper timed out | PARTIAL |
| Image/video | Yes | Current active profiles are null | NOT VERIFIED | Route exists, not run | UI/config only until configured |
| Document parsing / KB parsing | Yes | Source exposes persisted engine settings | NOT VERIFIED | Real test/install routes exist | PARTIAL |
| Tools/capabilities | Yes, but loading in smoke | Enabled tools returned in API | NOT VERIFIED | N/A | PARTIAL |
| Partners & agents | Yes | Renders subagent settings | NOT VERIFIED | N/A | PARTIAL |
| Memory | Route renders loading | NOT VERIFIED | NOT VERIFIED | N/A | PARTIAL |
| Status | Redirects to Settings hub | N/A | N/A | N/A | REDIRECT/ALIAS |
| Attachments/starters | Yes, loading in smoke | Source/API routes exist | NOT VERIFIED | N/A | PARTIAL |

### A5. End-To-End Journeys

| Journey | Result |
| --- | --- |
| Upload PDF -> create/select KB -> indexing -> grounded Tutor answer with citations | NOT VERIFIED in this run. Knowledge routes and RAG pipelines exist, and prior docs claim this passed, but this audit did not upload a PDF or verify citations in browser. |
| Trigger 9 chat quick actions | PARTIALLY VERIFIED by UI render only. `/home` renders quick actions beginning with Teach/Explain; the actual prompts and model responses were not sent in this run. |
| Generate quiz -> answer every type -> submit -> Progress/mastery/weak topics update | API-level path VERIFIED for quiz-result submission and weak-topic creation; full browser quiz generation across every type NOT VERIFIED. |
| STT -> chat -> TTS | TTS endpoint VERIFIED. STT browser microphone NOT VERIFIED. Active faster-whisper diagnostic FAILED/TIMED OUT in this run. Chat send not verified. |
| Book | Browser route renders; New book action not submitted. NOT VERIFIED end-to-end. |
| Co-writer | Browser route renders; draft creation/editing not tested. NOT VERIFIED end-to-end. |
| Partners | Browser route renders; partner chat/config not tested. NOT VERIFIED end-to-end. |
| Memory | Memory pages render; actual refresh/update lifecycle not tested. PARTIAL. |

Focused tests run:

```text
.\.venv\Scripts\python.exe -m pytest tests\api\test_voice_routes.py tests\api\test_settings_router.py::test_voice_provider_choices_include_global_engines tests\services\test_voice.py::test_resolve_tts_config_supports_global_edge_tts tests\services\test_voice.py::test_resolve_stt_config_supports_global_faster_whisper tests\services\test_voice_diagnostics.py -q
13 passed in 1.41s
```

```text
.\.venv\Scripts\python.exe -m pytest smarttutor\learning\tests\test_guided_mastery_updates.py tests\api\test_notebook_router.py::test_quiz_results_update_learning_progress -q
18 passed in 0.86s
```

TTS endpoint test:

```text
POST /api/v1/voice/tts with {"text":"Smart Tutor voice test."}
Output file: D:\project\deep-tutor\data\user\voice_audit\current_report_tts.mp3
Length: 15552 bytes
```

### A6. Contradictions Resolved

| Contradiction | Resolution |
| --- | --- |
| `D:\project\deep-tutor` vs `D:\project\smart-tutor` | `D:\project\deep-tutor` is real. `D:\project\smart-tutor` does not exist on this machine. |
| "Phase 1 docs only" vs STATUS implementation claims | The docs-only claim is obsolete. Runtime implementation work has landed in the dirty tree: `smarttutor/` source, API routers, voice adapters, learning services, and frontend Smart Tutor IA are present. |
| Voice report: no local Whisper/Piper/Windows adapters vs STATUS: global faster-whisper/Edge TTS work | Current code supports global/local voice adapters. Registry includes `global_edge_tts`, `global_piper`, `global_pyttsx3`, `global_gtts`, `windows_system_speech`, and `global_faster_whisper` in `smarttutor/services/voice/adapters/__init__.py:26-38`. Provider specs include Edge/Piper/Windows/pyttsx3/gTTS/faster-whisper in `smarttutor/services/config/provider_runtime.py:343-428`. However, current diagnostics show Edge TTS working and faster-whisper installed/configured but not working due to import timeout. |
| FEATURES says weak-topic unverified/partial, later says implemented/tested | The later implementation claim is true at API/test level. `smarttutor/api/routers/sessions.py:235` calls `LearningService.record_quiz_attempt`; `smarttutor/learning/service.py:128-160` creates `ErrorRecord` for wrong answers; `tests/api/test_notebook_router.py` verifies active error creation and later graduation. Full browser quiz E2E remains NOT VERIFIED. |
| Nav generic vs rebranded Smart Tutor IA | Current nav is already rebranded to My Library/Tutor/Practice/Revision/Progress. Source: `web/components/sidebar/SidebarShell.tsx:40-67`; browser smoke showed the same labels. |
| Exam/Test product exists? | No full standalone exam product was found. There is quiz/question-bank/mastery infrastructure and a Test quick-action prompt claim in docs, but no complete Google-Forms-style exam route/model/result lifecycle. |

## Part B - LangChain / LangGraph / RAG / Guardrails Investigation

### B1. Current Framework State

| Framework/library | Current state |
| --- | --- |
| LangChain | No dependency or source import found. `rg -n "langchain|langgraph" pyproject.toml requirements smarttutor tests web -S` found only suggestion-text examples in `smarttutor/services/suggestions.py` and tests. |
| LangGraph | Same: no runtime dependency/import. |
| LlamaIndex | Already a first-class dependency and RAG implementation. `pyproject.toml:49-54` includes `llama-index`, BM25 retriever, FAISS vector store; `smarttutor/services/rag/pipelines/llamaindex/pipeline.py:38` defines `LlamaIndexPipeline`. |
| GraphRAG | Optional extra. `pyproject.toml:223-231` defines `graphrag`; `smarttutor/services/rag/pipelines/graphrag/engine.py:1-8` isolates GraphRAG imports/version coupling. |
| LightRAG / RAG-Anything | Optional extra. `pyproject.toml:233-245` defines `rag-lightrag` via `raganything`; LightRAG server pointer support exists in `smarttutor/knowledge/kb_types.py:21-29` and `smarttutor/services/rag/pipelines/lightrag_server/__init__.py:1-4`. |
| Guardrails-style library | No `guardrails`, `outlines`, or `instructor` dependency found in app deps. The repo already uses Pydantic models and bespoke structured-output handling, especially around GraphRAG. |

What currently plays each framework role:

- Orchestration: `ChatOrchestrator` selects `context.active_capability or "chat"` and invokes a registered capability at `smarttutor/runtime/orchestrator.py:56-103`.
- Capability registry: built-ins are declared at `smarttutor/runtime/bootstrap/builtin_capabilities.py:4-10`; runtime registry is `smarttutor/runtime/registry/capability_registry.py:39`.
- Tool registry: `smarttutor/runtime/registry/tool_registry.py:21` defines `ToolRegistry`.
- Agent loop: `smarttutor/core/agentic/loop.py` implements the label/tool loop; `smarttutor/agents/chat/agentic_pipeline.py` is the main chat pipeline.
- Streaming: `smarttutor/core/stream.py` and `smarttutor/core/stream_bus.py` define and fan out shared stream events.
- Durable learning state: `smarttutor/learning/storage.py` and `smarttutor/learning/service.py` own persisted mastery/question state.
- RAG: `smarttutor/services/rag/pipelines/*` wraps LlamaIndex, GraphRAG, LightRAG, PageIndex, and external LightRAG server modes.
- Guardrails/validation: Pydantic request models appear throughout routers; GraphRAG structured response fallback and validation are in `smarttutor/services/rag/pipelines/graphrag/completion_adapter.py:51-128`.

### Recommendation

Do not do a wholesale LangChain/LangGraph rewrite now. The project already has a working native orchestration model, a typed event bus, settings/catalog plumbing, and RAG providers. A rewrite would create migration risk without fixing the product gaps found in Part A: incomplete Exam/Test mode, partially verified settings, and prompt-driven Practice/Revision quick actions.

Adopt selectively:

| Candidate | Recommendation | Why |
| --- | --- | --- |
| LangChain agents | Do not adopt as the primary chat loop now. | LangChain agents are now built over LangGraph and offer a generic harness, but Smart Tutor already has model/provider routing, tools, streaming, and capability registries. Replacing that would duplicate existing code. Official docs describe LangChain as a configurable agent framework built on LangGraph: https://docs.langchain.com/oss/python/langchain/overview |
| LangGraph | Consider for new long-running workflows only, especially Exam generation/review, Book generation, and durable multi-step imports. | LangGraph's best fit is durable execution, persistence, streaming, and human-in-the-loop workflows. Those are valuable for workflows that may pause, resume, or recover after failure, but not necessary for the current per-turn chat loop. Official docs: https://docs.langchain.com/oss/python/langgraph/overview and https://docs.langchain.com/oss/python/langgraph/persistence |
| Existing LlamaIndex | Keep and harden. | LlamaIndex is already integrated and documented around RAG, indexing, retrieval, structured extraction, and many integrations. The project should improve evaluation, citation verification, and ingestion UX before swapping frameworks. Official docs: https://developers.llamaindex.ai/python/framework/ |
| GraphRAG / LightRAG | Keep optional. | The code already treats these as heavy opt-in engines. This is correct because they have stricter model/embedding constraints and larger operational footprint. |
| Guardrails AI / validation library | Consider narrowly for Exam JSON generation and quiz schema validation, not as a global dependency. | Exam mode needs strict question/result schemas. Guardrails provides validators and structured-output validation concepts, but the project already uses Pydantic heavily. Start with Pydantic + provider structured output; add Guardrails only if retry/repair/validation policies become repetitive. Docs: https://guardrailsai.com/guardrails/docs and https://guardrailsai.com/guardrails/docs/concepts/validators |

Part B implementation guidance:

1. Keep `ChatOrchestrator`, `CapabilityRegistry`, `ToolRegistry`, `StreamBus`, and the current chat loop.
2. Build Exam/Test mode as deterministic product code first, with LLMs only generating question payloads and explanations.
3. Add a `structured_output` helper around Pydantic schemas for quiz/exam generation before adding a third-party guardrail dependency.
4. Add LangGraph only if a workflow needs durable checkpoints across server restarts or human pauses. Candidate: "generate exam from KB -> teacher/student review -> publish -> student attempts -> score -> remediation plan".
5. Add RAG evaluation tests before changing RAG engines: citation presence, answer-source consistency, retrieval hit rate on fixture docs, and no-source fallback behavior.

## Part C - Exam/Test Mode Investigation And Implementation Plan

### Current Exam/Test Reality

Confirmed: a proper Google-Forms-style Exam/Test product does not exist today.

What exists:

- Chat quick-action style Test is prompt-driven per `doc/SMART_TUTOR_FEATURES.md:926-934`.
- Deep-question/quiz generation exists as a capability.
- Quiz result submission exists at `POST /api/v1/sessions/{session_id}/quiz-results` in `smarttutor/api/routers/sessions.py:415-450`.
- Quiz submissions can update learning progress and create weak-topic `ErrorRecord`s through `smarttutor/api/routers/sessions.py:184-246` and `smarttutor/learning/service.py:128-160`.
- Question Bank/Practice UI exists at `/space/questions`; browser smoke showed empty-state controls.
- Book quiz blocks exist and can self-grade choice questions; source: `web/app/(workspace)/book/components/blocks/QuizBlock.tsx`.

What is missing:

- No dedicated `/exam` or `/tests` student route was found under `web/app`.
- No persisted `Exam`, `ExamQuestion`, `ExamAttempt`, or `ExamResult` model was found.
- No one-question-at-a-time exam runner with radio buttons, answer review, submit confirmation, scoring page, saved history, or remediation plan was verified.
- No exam timer, marks, sections, teacher/published state, or attempt lifecycle was found.

### Product Shape

Build a real Exam/Test mode as a deterministic assessment workflow:

- Student opens `/space/exams` or `/exams`.
- Student sees available exams and can start one.
- Attempt page supports one-question-at-a-time and scroll-list layouts.
- MCQ questions use radio buttons; future types can add checkbox, short answer, numeric, matching.
- Student selections are saved locally and optionally autosaved server-side.
- Submit shows confirmation if unanswered questions remain.
- Results page shows total score, per-question correct/incorrect, chosen answer, correct answer, explanation, source/citation when generated from KB, and next practice/revision links.
- Wrong answers create learning attempts/errors using the existing `LearningService`.

### Data Model

Add `smarttutor/exams/models.py`:

- `Exam`: `id`, `title`, `description`, `source_refs`, `status`, `settings`, `created_at`, `updated_at`.
- `ExamQuestion`: `id`, `exam_id`, `order`, `question_type`, `prompt`, `options`, `correct_answer`, `explanation`, `difficulty`, `concentration`, `knowledge_context`, `source_citations`, `marks`.
- `ExamAttempt`: `id`, `exam_id`, `session_id`, `started_at`, `submitted_at`, `status`, `answers`, `score`, `max_score`.
- `ExamAnswer`: `question_id`, `selected_option`, `is_correct`, `awarded_marks`.
- `ExamResult`: `attempt_id`, `score`, `max_score`, `percent`, `per_question`, `learning_progress_result`.

Use Pydantic for transport models and SQLite for persistence, mirroring `LearningStore` and `SQLiteSessionStore`.

### Backend Plan

Add `smarttutor/api/routers/exams.py` mounted at `/api/v1/exams`.

Endpoints:

- `GET /api/v1/exams`: list exams.
- `POST /api/v1/exams/generate`: generate an exam from topic, KB refs, file refs, or question-bank refs.
- `GET /api/v1/exams/{exam_id}`: exam metadata and questions, without correct answers unless in author/admin preview mode.
- `POST /api/v1/exams/{exam_id}/attempts`: start attempt.
- `PUT /api/v1/exams/{exam_id}/attempts/{attempt_id}/answers/{question_id}`: autosave selected answer.
- `POST /api/v1/exams/{exam_id}/attempts/{attempt_id}/submit`: score deterministically and persist result.
- `GET /api/v1/exams/{exam_id}/attempts/{attempt_id}/result`: result page payload.

Scoring:

- MCQ: exact option-key match.
- Multiple-select later: set equality.
- Short-answer later: LLM judge through existing quiz judge, but mark as "AI-graded" and store rubric/judgment.
- On submit, translate each answer into `QuizAttempt`-like learning records so existing mastery/weak-topic logic is reused.

### Frontend Plan

Add routes:

- `web/app/(utility)/space/exams/page.tsx`: exam list/history.
- `web/app/(workspace)/exam/[examId]/page.tsx`: attempt runner.
- `web/app/(workspace)/exam/[examId]/result/[attemptId]/page.tsx`: results.

Components:

- `ExamList`
- `ExamGeneratorPanel`
- `ExamRunner`
- `ExamQuestionCard`
- `ExamNavigationRail`
- `ExamSubmitDialog`
- `ExamResultSummary`
- `ExamReviewQuestion`

Controls:

- Radio buttons for MCQ.
- Progress indicator: answered/unanswered count.
- Previous/Next buttons.
- Question palette for jump navigation.
- Submit button disabled or confirmed when unanswered remain.
- Results actions: "Practice wrong answers", "Start revision", "Ask Tutor about this question".

### Integration With Existing Systems

- Store wrong answers into learning progress via the same `LearningService.record_quiz_attempt` pathway used by session quiz results.
- Add wrong questions to the Question Bank so `/space/questions` becomes the Practice entry point.
- Link results to `/space/learning` for revision plans.
- If generated from KB, carry `source_citations` from RAG retrieval into each question and display them on the result page.
- Add `exam_attempt_id` to session metadata when the Tutor is opened from an exam question.

### Tests

Backend:

- Create/list exam.
- Generate exam validates schema and rejects malformed LLM output.
- Start attempt hides correct answers.
- Autosave answer persists.
- Submit computes score and is idempotent.
- Wrong answer creates active `ErrorRecord`.
- Later correct attempts can graduate the weak topic.

Frontend:

- Exam list renders.
- MCQ radio selection persists across navigation.
- Submit confirmation appears with unanswered questions.
- Results page shows correct/incorrect states and total score.
- "Practice wrong answers" navigates with selected question-bank refs.

E2E:

- Generate exam from fixture topic.
- Answer one correct and one wrong.
- Submit.
- Verify score.
- Verify result details.
- Query learning store and confirm an error record exists for the wrong answer.

### Delivery Sequence

1. Add exam models and SQLite store.
2. Add backend CRUD/start/submit/result endpoints.
3. Add deterministic MCQ-only UI runner and result page.
4. Wire wrong answers into learning progress and question bank.
5. Add exam generation from existing `deep_question`/quiz schema.
6. Add source citation carry-through for KB-generated exams.
7. Add timed sections, multiple-select, matching, numeric, and short-answer grading after MCQ is stable.

### Final Verdict

Smart Tutor is no longer a docs-only transformation. It is a runnable, partially rebranded tutoring app with real chat infrastructure, settings/catalog infrastructure, RAG providers, voice endpoints, and quiz-to-learning persistence. The biggest product gap is not lack of LangChain; it is the absence of a deterministic Exam/Test product and the incomplete verification/polish of visible student workflows. Build Exam/Test mode directly on the current architecture, use Pydantic and the existing learning store first, and introduce LangGraph/Guardrails only where they solve a concrete durability or validation problem.
