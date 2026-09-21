# Practice / Background / Foreground Investigation

Date: 2026-09-10  
Workspace: `D:\project\deep-tutor`  
Scope: read-only implementation and integration audit. No application code was changed.

## 1. Executive Summary

Smart Tutor does not currently contain clearly named first-class features called `Background` or `Foreground`. In the current codebase, those words mostly appear as CSS/theme terms or internal background work. The closest real implementation is:

- `Practice`: split across chat quick actions, mastery/revision, question bank, quiz/exam, and Playground capability testing.
- `Background`: L1/L2/L3 memory context, knowledge/RAG context, selected past sessions/notes/questions, and backend background jobs such as memory consolidator runs.
- `Foreground`: the active user-facing chat/playground/exam/memory workbench execution surface.

The specific observed flow, "select a model and press Run, but nothing happens," does not map to a dedicated `Practice` route. The only audited UI that has both a model selector and a `Run` button is the Memory L2/L3 `LLM workspace` in `MemoryRunPanel`. That flow is connected from frontend to backend. As of 2026-09-11, no-op, invalid selected model, and total model failure states are visible instead of silently falling through.

Most important finding: the `Run` path is not disconnected. The remaining product gap is that L2/L3 memory only becomes useful after an intentional Memory Run builds derived docs from L1 evidence.

## 2. Current Project Architecture

Frontend:

- Next.js app under `web/`.
- Primary chat route: `web/app/(workspace)/home/[[...sessionId]]/page.tsx`.
- Practice-adjacent routes:
  - `/home`: Tutor/chat with learning quick actions, model selector, knowledge/memory/question selectors.
  - `/space/learning`: mastery/revision dashboard.
  - `/space/questions`: question bank.
  - `/exam`: autonomous exam workflow.
  - `/playground`: direct tool/capability execution.
  - `/memory`, `/memory/l1`, `/memory/l2`, `/memory/l3`: memory workbench.

Backend:

- FastAPI app under `smarttutor/api/`.
- Main endpoints relevant to this audit:
  - `/api/v1/ws`: unified chat WebSocket.
  - `/api/v1/learning/*`: mastery/revision progress.
  - `/api/v1/question*`: question generation/bank.
  - `/api/v1/exam/*`: autonomous exam.
  - `/api/v1/memory/*`: L1/L2/L3 memory and consolidator runs.
  - `/api/v1/plugins/*`: Playground tool/capability execution.
  - `/api/v1/settings/llm-options`: selectable LLMs.

Storage:

- The project intentionally uses file/JSON-backed runtime storage under `data/`, not a central SQL database for these flows.
- Memory paths are resolved per user. The memory layout is documented in `smarttutor/services/memory/paths.py`.

## 3. Practice

### Intended Purpose

Practice is meant to let a student work on material actively: get targeted drills, answer questions, receive feedback, continue mastery/revision, and track progress.

### Current UI

There is no standalone `/practice` route. Practice exists as several surfaces:

- Chat quick action `Practice` in `web/app/(workspace)/home/[[...sessionId]]/page.tsx`. It injects a prompt: "Give me targeted practice on the selected material..."
- Mastery/revision dashboard at `/space/learning` in `web/app/(utility)/space/learning/page.tsx`.
- Question bank at `/space/questions`.
- Exam mode at `/exam`.
- Playground capability tester at `/playground`, including `deep_question`, `mastery_path`, and general chat/capability execution.

### Frontend Flow

Chat practice quick action:

1. User chooses the `Practice` quick action in `/home`.
2. The prompt is sent through the normal chat composer path.
3. Selected model, knowledge bases, memory files, question bank entries, book references, sessions, and agents are included through the same chat state as ordinary Tutor messages.
4. Transport is the unified chat/WebSocket path.

Mastery/revision:

1. `/space/learning` calls `fetchAllProgress()` → `GET /api/v1/learning/progress`.
2. Selecting a path calls `fetchMasteryMap(pathId)` → `GET /api/v1/learning/progress/{pathId}/map`.
3. Activity polling calls `GET /api/v1/learning/progress/{pathId}/events`.
4. `Continue tutoring in Chat` opens a chat URL produced by `newMasteryPathChatUrl(pathId)`.

Memory run surface:

1. `/memory/l2/*` or `/memory/l3/*` renders `MemoryRunPanel`.
2. Model selector loads via `listLLMOptions()`.
3. Run button calls `handleRun()`.
4. `handleRun()` calls `useMemoryRun.start()`.
5. `start()` posts to `POST /api/v1/memory/runs/start`.
6. Frontend attaches to `GET /api/v1/memory/runs/{id}/events?since=0`.
7. Events render in the LLM trace panel.

### Backend Flow

Mastery backend:

- `smarttutor/api/routers/mastery_path.py` exposes progress/map/events/objective/mutation endpoints.
- `smarttutor/capabilities/mastery/capability.py` marks turns as `mastery_path` and runs the standard `AgenticChatPipeline`.
- `smarttutor/capabilities/mastery/loop.py` mounts mastery tools and handles pause/resume quiz answers.
- `smarttutor.learning` owns deterministic mastery gates and progress storage.

Memory run backend:

- `POST /api/v1/memory/runs/start` in `smarttutor/api/routers/memory.py`.
- Valid modes: `update`, `audit`, `dedup`, and backend-only `merge`.
- `RunManager` in `smarttutor/services/memory/consolidator/runs.py` owns cancellable background tasks and event replay.
- LLM calls go through `smarttutor/services/memory/consolidator/modes/_runtime.py`.

Playground backend:

- `GET /api/v1/plugins/list` lists tools/capabilities.
- `POST /api/v1/plugins/tools/{tool}/execute-stream` runs one tool.
- `POST /api/v1/plugins/capabilities/{capability}/execute-stream` runs a capability through `ChatOrchestrator`.

### Model Flow

Shared model selection is exposed by `/api/v1/settings/llm-options`.

For memory runs:

- Frontend sends `llm_selection: { profile_id, model_id }`.
- Backend passes it into `run_update`, `run_audit`, or `run_dedup`.
- Those modes call the shared memory-run activation helper, which delegates to `activate_llm_selection()`.
- If selection cannot be resolved, the run now fails visibly instead of continuing with the default model.
- Valid explicit selections emit a `model_selected` run event with provider/model details.

For mastery/chat:

- Model selection is handled by the normal chat runtime.
- Mastery is not a separate model pipeline; it is an agentic chat mode with mastery tools.

For exam:

- `ExamGeneratorModal` uses the shared selector and sends `llm_selection` to `/api/v1/exam/generate`.

### Memory Flow

Practice uses memory in two distinct ways:

- Chat/Tutor can attach selected memory files as context through the composer.
- Memory workbench runs use the selected model to consolidate L1 traces into L2/L3 markdown memory.

Mastery progress remains authoritative in `LearningStore`, and Memory now reads a summarized LearningStore snapshot through the existing `quiz` L1 surface.

### RAG Flow

Chat practice and Playground capabilities can use RAG when knowledge bases are selected and the relevant tool is enabled. The memory run panel itself is not a RAG query surface; it consolidates memory documents from trace/document sources.

### Storage

- Mastery/revision progress: `LearningStore` under `data/`.
- Exam specs/results: `data/user/exams/`.
- Memory:
  - L1 traces: `memory/trace/<surface>/<YYYY-MM-DD>.jsonl`.
  - L2 docs: `memory/L2/<surface>.md`.
  - L3 docs: `memory/L3/<recent|profile|scope|preferences>.md`.
- Playground configs: frontend local storage via `web/lib/playground-config.ts`.

### Current Status

Practice is `PARTIALLY IMPLEMENTED` as a product concept, because it is spread across working features rather than one coherent Practice surface.

Working parts:

- Chat prompt-based practice.
- Mastery/revision dashboard and backend.
- Exam mode.
- Question bank surfaces.
- Playground direct capability execution.

Incomplete or unclear:

- No explicit `/practice` route.
- No single Practice UI contract that defines background/foreground/memory options.
- No clear user-facing distinction between "practice", "exam", "quiz", "revision", and "question bank".

### Reproduction of "Run does nothing"

Safe verification performed:

- Confirmed local ports listening: frontend `3782`, backend `8001`, Ollama `11434`.
- HTTP checks returned `200` for:
  - `http://localhost:8001/api/v1/memory/overview`
  - `http://localhost:8001/api/v1/learning/progress`
  - `http://localhost:3782/playground`
- Source traced the model-select + Run path in `MemoryRunPanel` to `POST /api/v1/memory/runs/start`.
- Targeted tests passed:
  - Python: `39 passed` for memory runs/modes, mastery capability, and question-bank API.
  - Node: `610 passed` through `npm run test:node -- mastery-path-activity.test.ts chat-launch-intent.test.ts capability-access.test.ts quiz-question-type.test.ts`.

NOT VERIFIED:

- I did not click a live model-backed memory `Run` against real user memory, because that can mutate memory documents and spend model tokens. This was a read-only audit.

### Root Cause

There is no evidence of a completely disconnected Run handler in the audited code. The most likely root causes for "Run does nothing" are:

1. The user may be using the Memory L2/L3 `LLM workspace`, not a dedicated Practice screen.
2. Memory runs can legally end with no visible edits, especially if no new L1/L2 input exists.
3. Previously, total LLM failure in the consolidator could return `""`; this is fixed as of 2026-09-11, and total LLM failure now errors the run.
4. Previously, invalid or unavailable selected models could be logged and ignored; this is fixed as of 2026-09-11, and explicit invalid selections now fail the run.
5. The UI trace can still show only system/no-op events when there is no new input, but it now labels no-op/no-doc/no-change outcomes.

### Evidence

- `web/components/memory/MemoryRunPanel.tsx`: `handleRun()` sends mode, budget/iterations, language, and `llmSelection`.
- `web/components/memory/useMemoryRun.ts`: `POST /api/v1/memory/runs/start`, then event attachment via `/events`.
- `smarttutor/api/routers/memory.py`: `start_run()` validates layer/key and starts `RunManager`.
- `smarttutor/services/memory/consolidator/modes/_runtime.py`: fallback LLM failure now raises after both streaming and non-streaming paths fail.
- `smarttutor/services/memory/consolidator/modes/update.py`, `audit.py`, `dedup.py`: unresolvable explicit `llm_selection` now fails the run.

## 4. Background

### Intended Purpose

The project does not define a product feature named `Background`. Based on implementation, the practical "background" layer is supporting context and asynchronous work:

- Memory L1/L2/L3 context.
- Selected previous sessions, notebook records, question bank entries, books, and knowledge bases.
- RAG/knowledge context.
- Backend background tasks such as memory consolidation.

### Implementation

Actual implementation areas:

- Memory traces and documents in `smarttutor/services/memory`.
- Memory workbench routes in `web/app/(utility)/memory/*`.
- Chat context pickers in `web/app/(workspace)/home/[[...sessionId]]/page.tsx` and `web/components/chat/home/ChatComposer.tsx`.
- Background run manager in `smarttutor/services/memory/consolidator/runs.py`.
- Background model discovery/cache behavior referenced in existing docs and tests.

### Integration

Memory/background context can reach model execution through chat context selection and memory tools. Memory consolidation runs are background backend tasks with frontend SSE replay.

### Current Status

`PARTIALLY IMPLEMENTED`.

There is strong implementation for memory and asynchronous backend runs, but no explicit Background UI/mode with a documented user-facing contract.

### Problems

- "Background" is not named or explained to users as a coherent feature.
- Some background failures are intentionally swallowed or softened to protect the user flow, but the UI does not always surface enough detail.
- There is no single matrix showing which background context sources affect which model call.

## 5. Foreground

### Intended Purpose

The project does not define a product feature named `Foreground`. The practical foreground is the active user-facing execution surface:

- The open chat turn.
- The current Playground tester run.
- The current Exam runner.
- The current Memory L2/L3 workbench run trace.

### Implementation

Actual implementation areas:

- Chat UI and WebSocket flow in `/home`.
- Playground testers in `web/app/(workspace)/playground/page.tsx`.
- Exam runner in `/exam`.
- Memory workbench in `/memory/l2` and `/memory/l3`.

### Integration

Foreground actions call backend endpoints or WebSockets directly and display streamed events/results.

### Current Status

`WORKING` as a general architecture pattern, but `NOT IMPLEMENTED` as a named feature.

### Problems

- No explicit foreground/background toggle or semantic distinction exists in the code.
- If the intended product design requires choosing "foreground memory" vs "background memory", that UI/API contract is missing.

## 6. Memory Integration

### L1

Purpose: raw event capture.

- Defined in `smarttutor/services/memory/trace.py`.
- Stored as append-only JSONL under `memory/trace/<surface>/<YYYY-MM-DD>.jsonl`.
- Surfaces: `chat`, `notebook`, `quiz`, `kb`, `book`, `partner`, `cowriter`.
- Writes are logged-and-swallowed on failure so user flows are not broken by memory capture.

Status: `WORKING`, with intentional best-effort failure handling.

### L2

Purpose: per-surface summarized memory.

- Defined in `smarttutor/services/memory/paths.py`.
- Stored under `memory/L2/<surface>.md`.
- Produced by LLM-driven consolidator runs from L1 events.
- Editable and resettable from the memory workbench.

Status: `WORKING`, environment dependent on model availability for Update/Audit/Dedup.

### L3

Purpose: cross-surface memory slots.

- Slots: `recent`, `profile`, `scope`, `preferences`.
- Stored under `memory/L3/<slot>.md`.
- Built from L2 docs except `preferences`, which is written by the `write_memory` tool and guarded from ordinary update/audit runs.

Status: `WORKING`, with special-case restrictions for `preferences`.

### Practice → Memory Flow

Current practice-like chat can use memory when the user selects memory files or when memory tools are mounted by the chat runtime. Mastery progress itself stays authoritative in LearningStore, but a compact summary of LearningStore paths is now visible to Memory through the existing `quiz` L1 surface.

There is no direct evidence that `/space/learning` automatically injects L2/L3 memory into every mastery turn. The mastery turn uses the normal chat pipeline and mounted tools.

## 7. Model Selection

### Providers

Current documented/configured providers include OpenAI, Ollama, Krutrim, and other OpenAI-compatible profiles through the model catalog.

### Model Selection Flow

Frontend:

- `listLLMOptions()` calls `/api/v1/settings/llm-options`.
- Chat, Exam, and Memory workbench use shared LLM option types.

Backend:

- Settings router resolves model catalog data.
- Runtime model selection resolves through provider/runtime config.
- Memory consolidator modes install scoped selected LLM config when possible.

### Actual Runtime Model

- Chat and Exam: selected model is intended to reach backend runtime.
- Memory Run: selected model is sent in `llm_selection` and activated by the consolidator mode.
- Playground: capability tester currently does not expose the same model selector in the generic capability UI; it uses runtime/default model unless capability config or backend runtime supplies otherwise.

### Problems

- DONE 2026-09-11: Memory run model selection no longer falls back silently when an explicit selection is invalid/unavailable.
- Playground capability tester has Run/Send/Generate buttons but no obvious shared model selector for every capability.
- The user phrase "select model and press Run" most likely points to memory workbench, not a dedicated Practice UI.

## 8. RAG / Knowledge Integration

Working paths:

- Chat composer can attach selected knowledge bases.
- Playground capability tester enables optional tools, including RAG when listed for the capability.
- Exam generation can be grounded in a selected knowledge base.
- Existing docs report verified live browser RAG and Exam generation.

Limitations:

- Memory consolidation is not a RAG search surface.
- Practice quick action in chat uses whatever knowledge context is selected; it is not a separate practice-specific RAG pipeline.
- Foreground/Background do not exist as named RAG modes.

## 9. Data / Storage

Storage found:

- Memory: markdown and JSONL files under per-user memory root.
- Mastery/revision: `LearningStore` file-backed progress/interactions/events.
- Exams: `data/user/exams/`.
- Model/settings: `data/user/settings/*.json` and YAML settings.
- Playground config: browser local storage.
- Question bank/notebook/session data: project data services, not a practice-specific SQL model.

Practice results/progress are persisted only in specific systems:

- Mastery attempts and progress: yes.
- Exam attempts/results: yes.
- Chat quick-action practice: as normal chat/session data, not as structured practice progress.
- Playground test runs: generally not durable except local config/history visible in the UI state.

## 10. Error Handling

Findings:

- Memory trace append failures are logged and swallowed by design.
- Memory consolidator event consumer failures are debug-logged and swallowed.
- Memory LLM streaming failures fall back to non-streaming; if fallback also fails, the run errors and emits an `llm_io_end` error event.
- Memory run start errors are surfaced in the MemoryRunPanel error row.
- Backend `RunManager` catches task exceptions, marks run `error`, and emits an error event.
- `/space/learning` list/map fetch failures collapse to empty/null states without detailed UI errors.
- `/exam` uses direct `fetch()` instead of shared `apiFetch()`, so auth/error behavior is less consistent with other frontend surfaces.
- Playground displays SSE `error` events in the assistant panel.

Current UX gap: no-op model runs are now labeled, and invalid selected-model fallback is fixed. A browser-level fixture test for the visible timeline is still not implemented.

## 11. Security Findings

Lightweight findings only:

- Memory doc keys are validated against known L2 surfaces/L3 slots.
- Learning `book_id` rejects path traversal characters.
- Plugin/capability execution accepts user content and attachments; backend routes are auth-gated in `main.py`.
- Model names/profile IDs are user-controlled from UI payloads but resolved server-side.
- Memory reset deletes files, but it is explicit and refuses active runs.
- L1 trace writes intentionally swallow failures; this protects UX but can hide audit/storage failures.
- RAG and memory content are untrusted model context. Prompt/context injection remains a realistic risk, though existing docs report a live prompt-injection test for RAG.

No destructive security testing was performed.

## 12. Feature Status Matrix

| Feature | Frontend | Backend | Integration | Model | Memory | RAG | Storage | Status | Evidence |
| ------- | -------- | ------- | ----------- | ----- | ------ | --- | ------- | ------ | -------- |
| Chat Practice quick action | Exists in `/home` | Normal chat runtime | Connected through chat composer/WebSocket | Uses selected chat model | Can include selected memory/context | Can include selected KB | Chat/session storage | WORKING | `learningActions` includes `Practice`; normal chat flow |
| Dedicated Practice page | No `/practice` route | No dedicated API | None | None | None | None | None | NOT IMPLEMENTED | Route list has no practice page |
| Mastery/revision practice | `/space/learning` | `/api/v1/learning/*` | Connected | Uses chat runtime when continuing | Separate from L1/L2/L3, can use chat tools | Via chat/RAG when used | `LearningStore` | WORKING | `mastery_path.py`, `MasteryPathCapability`, tests passed |
| Question bank | `/space/questions` | `/api/v1/question*` and question notebook APIs | Connected | Generation paths use model services | Question surface contributes L1 `quiz` traces | Can use source material depending path | Data files/services | WORKING | Question bank API tests passed |
| Exam mode | `/exam` | `/api/v1/exam/*` | Connected | Shared selector in generator | Feeds learning progress | KB-grounded generation supported | `data/user/exams` | WORKING | Existing docs plus source; direct fetch error handling caveat |
| Memory L2/L3 Run | `/memory/l2`, `/memory/l3` | `/api/v1/memory/runs/start` and `/events` | Connected | Selected model passed as `llm_selection` | Core feature | No direct RAG search | Markdown docs + run history in memory | PARTIALLY IMPLEMENTED | Connected, but no-op/model-failure visibility weak |
| Playground tool Execute | `/playground` | `/api/v1/plugins/tools/{name}/execute-stream` | Connected | Tool-dependent | Tool-dependent | Tool-dependent | UI state/process logs | WORKING | Source trace |
| Playground capability Run/Send | `/playground` | `/api/v1/plugins/capabilities/{name}/execute-stream` | Connected | Uses runtime/default; no universal selector | Capability-dependent | Capability-dependent | Local config only | PARTIALLY IMPLEMENTED | Connected, but model selector not universal |
| Background as named feature | No explicit UI | No explicit service | Not defined | Not defined | Memory/background jobs exist | KB context exists | Mixed | REFERENCED BUT NOT IMPLEMENTED | Term not semantically defined in code |
| Foreground as named feature | No explicit UI | No explicit service | Not defined | Not defined | Active context only | Active context only | Mixed | REFERENCED BUT NOT IMPLEMENTED | Term not semantically defined in code |
| L1 memory | `/memory/l1` | `/api/v1/memory/trace/*` | Connected | No model execution | Raw traces | No | JSONL | WORKING | `trace.py`, `paths.py` |
| L2 memory | `/memory/l2` | `/api/v1/memory/doc/L2/*` | Connected | Consolidator uses selected/default LLM | Per-surface docs | No direct RAG | Markdown | WORKING / ENVIRONMENT DEPENDENT | Model required for update/audit/dedup |
| L3 memory | `/memory/l3` | `/api/v1/memory/doc/L3/*` | Connected | Consolidator uses selected/default LLM | Cross-surface docs | No direct RAG | Markdown | WORKING / ENVIRONMENT DEPENDENT | `preferences` guarded |

## 13. What Is Working

- Frontend and backend are currently reachable locally on ports `3782` and `8001`.
- Memory overview endpoint works.
- Learning progress endpoint works.
- Playground page loads.
- Memory run frontend-to-backend path is wired.
- Mastery/revision backend and frontend API client are wired.
- Exam mode is implemented and documented as verified.
- Existing targeted Python tests passed.
- Existing Node tests passed.

## 14. What Is Broken

No hard break was proven in read-only verification.

Likely broken/weak behaviors:

- User-facing Practice is fragmented; no dedicated feature contract.
- "Background" and "Foreground" are not real named features.
- Memory run can still be a legitimate no-op when there is no new input, but the UI now labels no-op/no-doc/no-change outcomes.
- Invalid selected model fallback during memory consolidation is fixed; explicit invalid selections now fail visibly.
- `/space/learning` suppresses detailed load errors into empty/null UI states.
- Exam page uses raw `fetch`, not the shared API helper.

## 15. What Is Missing

- A dedicated Practice page or clear product entry point, if that is intended.
- A clear UI/API definition for Background and Foreground.
- DONE 2026-09-11: A visible no-op/no-doc/no-change result state for memory runs.
- DONE 2026-09-11: selected-model truthfulness for Memory Run; invalid explicit selections fail instead of falling back.
- A documented map of which context sources affect which model requests.
- Focused Playwright test for "select model → Run → visible run trace/result" on a safe fixture.

## 16. What These Features Are Supposed To Provide

Practice should provide structured active learning: targeted exercises, quizzes, feedback, progress, and adaptive next steps.

Background should provide the tutor with continuity: memory, prior work, knowledge bases, sessions, and persistent learner context.

Foreground should provide the active task surface: the thing the student is doing right now, such as chat, exam, playground run, or memory consolidation.

How they currently work together:

Student uses chat/practice/exam/mastery → selects model/context where available → backend uses chat/runtime/capability services → memory/RAG may be mounted depending on surface → response/progress is displayed and sometimes persisted.

This architecture exists, but not under explicit Background/Foreground product names.

## 17. Benefits

Current benefits:

- Practice quick actions reduce prompt setup.
- Mastery/revision tracks progress and gates advancement.
- Exam mode creates and grades autonomous MCQ exams.
- Memory L1/L2/L3 gives continuity across sessions.
- Model selection lets users route work to local or cloud models.
- RAG grounds answers in uploaded/selected knowledge.

Potential benefits:

- A unified Practice surface could make drills, exams, revision, memory, and RAG feel coherent.
- Explicit Background/Foreground controls could help users understand what context is being used now versus saved for later.
- Better no-op/error visibility would reduce confusion and support safer model switching.
- A repeatable smoke test for Run flows would catch regressions early.

## 18. Prioritized Fix Plan

### P0 — Blocking

No P0 confirmed in this audit. The app and audited endpoints are reachable, and key tests pass.

### P1 — Important

Problem: Memory `Run` can appear to do nothing. RESOLVED FOR BACKEND/UI STATUS on 2026-09-11.  
Root cause: no-op runs, empty LLM responses, and selected-model fallback were not surfaced clearly.  
Affected files: `web/components/memory/MemoryRunPanel.tsx`, `web/components/memory/useMemoryRun.ts`, `smarttutor/services/memory/consolidator/modes/_runtime.py`, `update.py`, `audit.py`, `dedup.py`.  
Affected route/component: `/memory/l2/*`, `/memory/l3/*`, `MemoryRunPanel`.  
Affected backend endpoint/service: `POST /api/v1/memory/runs/start`, `GET /api/v1/memory/runs/{id}/events`, memory consolidator.  
Implemented fix: render explicit statuses for `no_new_input`, `no_doc`, and no-change outcomes; emit `model_selected`; fail invalid explicit selections; error total LLM failure.  
Dependencies: existing SSE event stream.  
Risk: low-medium.  
How to test: safe fixture memory doc; fake/monkeypatched model failure; Playwright fixture for visible status remains recommended.  
Expected result: pressing Run produces a clear visible outcome for no-op/error/model-selection cases.  
Benefit: removes the "nothing happens" experience.

Problem: Practice is fragmented.  
Root cause: practice exists as chat prompt, mastery, question bank, exam, and playground without one product contract.  
Affected files: `/home`, `/space/learning`, `/space/questions`, `/exam`, `/playground`, docs/navigation.  
Proposed fix: document and optionally add a Practice hub that links existing features instead of rewriting them.  
Dependencies: existing routes.  
Risk: low.  
How to test: route crawl and link validation.  
Expected result: users know where to practice and which mode to choose.  
Benefit: clearer student workflow.

### P2 — Quality

Problem: `/space/learning` hides detailed load failures.  
Root cause: catch blocks set empty/null state.  
Affected files: `web/app/(utility)/space/learning/page.tsx`, `web/lib/learning-api.ts`.  
Proposed fix: add visible error banner with retry while keeping empty state for real empty data.  
Risk: low.  
How to test: mock failed `GET /api/v1/learning/progress`; verify error state.

Problem: Exam page uses raw `fetch`.  
Root cause: older code path did not adopt `apiFetch`.  
Affected files: `web/app/(workspace)/exam/page.tsx`, `web/components/exam/ExamGeneratorModal.tsx`.  
Proposed fix: move to `apiFetch(apiUrl(...))` for consistent auth/proxy/error behavior.  
Risk: low.  
How to test: existing exam tests plus auth/error mock.

Problem: Background/Foreground not documented.  
Root cause: names are not implemented as features.  
Affected files: docs and future UX copy.  
Proposed fix: either remove those labels or define them explicitly as context layers.  
Risk: low.  
How to test: docs/link review.

### P3 — Optional Enhancement

Problem: Playground capability tester lacks universal model selection.  
Root cause: it executes capabilities through `ChatOrchestrator` without a shared selector in the generic tester.  
Affected files: `web/app/(workspace)/playground/page.tsx`, `smarttutor/api/routers/plugins_api.py`.  
Proposed fix: add optional shared LLM selector to capability tester and pass `llmSelection`.  
Risk: medium.  
How to test: network payload verification and backend selected-model assertion.

## 19. Recommended Implementation Order

1. DONE 2026-09-11: Add visible Memory Run no-op/error statuses and selected-model truthfulness.
2. PARTIAL 2026-09-11: Added focused backend fixture tests for valid/invalid selected model and L3 synthesis. A Playwright UI fixture remains open.
3. Clarify Practice navigation/documentation using existing routes.
4. Add error banners/retry states to `/space/learning`.
5. Convert Exam raw fetches to shared API helper.
6. Decide whether Background/Foreground are product labels; if yes, define their UX contract before building new code.
7. Consider universal Playground model selector after the main Run confusion is fixed.

## 20. Verification Plan

For Memory Run:

- DONE/PARTIAL: Unit tests cover valid selected-model event, invalid selected-model failure before LLM, L2 update, L3 profile synthesis, no-new-input, audit, and dedup. Direct model-failure and no-doc tests are still worth adding.
- Frontend component test or Playwright test that `MemoryRunPanel` renders those states remains open.
- Playwright test against a disposable fixture memory root.

For Practice:

- Route crawl for `/home`, `/space/learning`, `/space/questions`, `/exam`, `/playground`.
- Verify each primary button sends a request or navigates.
- Verify empty/error/loading states.

For model selection:

- Mock `/api/v1/settings/llm-options`.
- Verify selected model appears in request payload.
- Backend test that selected model reaches runtime config.
- DONE: Negative backend test for invalid model shows error instead of fallback. Browser-visible assertion remains open.

For RAG:

- Fixture KB query through chat/practice prompt.
- Verify selected KB name appears in request payload and retrieval events.

For storage:

- Verify learning progress changes after mastery/exam attempts.
- Verify memory L1/L2/L3 paths update only in tests using disposable data roots.

## 21. Documentation / Maintenance Notes

- Keep "Practice" documentation grounded in the actual routes until a dedicated Practice feature exists.
- Do not describe Background/Foreground as implemented features unless product/UX code is added.
- When documenting memory, use the project definitions:
  - L1 = append-only raw trace.
  - L2 = per-surface markdown memory.
  - L3 = cross-surface markdown memory slots.
- Any future fix should prefer existing APIs and event streams over new infrastructure.
- Avoid mutating real user memory during verification; use fixture data roots or mocked model calls.

## 22. What Smart Tutor Tracks About the Student

Smart Tutor currently tracks several kinds of student activity. The important distinction is that some data is durable learning/product state, while some is only optional context for model calls.

Tracked locally:

- Conversations: chat sessions, messages, session titles, selected tools, selected knowledge bases, selected model, selected memory refs, selected books/notebooks/questions, persona, capability, attachments metadata, and request snapshots.
- Files and documents: uploaded/attached files, extracted document text, notebooks, co-writer documents, books, and knowledge-base documents/index metadata.
- Knowledge bases and RAG: knowledge base names, descriptions, RAG provider, index versions, document inventory, retrieval/search traces, and indexed document chunks under the configured RAG pipeline.
- Practice/questions: quiz/question-bank rows, question text, question type, options, correct answer, explanation, user answer, correctness, difficulty, bookmarks, and follow-up context.
- Exams: generated exam specs, questions, answers, citations, submitted answers, score, percentage, time spent, topic breakdown, and per-question result records.
- Mastery/progress: mastery paths, modules, knowledge points, stages, mastery levels, quiz attempts, error records, pending questions, interaction status, review queue, spaced-repetition state, and path events.
- Memory: L1 workspace snapshot entities, L1 trace events, L2 per-surface markdown facts, L3 cross-surface markdown slots, and memory-run metadata.
- Settings/preferences: model catalog selections, memory consolidator settings, starter-suggestion trace count, UI/language/tool settings, voice provider settings, attachment limits, and feature/tool toggles.
- Suggestions/recent activity: cached starter suggestions derived from L3 memory plus recent activity labels.
- Partner/tutor interactions: partner sessions, partner memory tools, and partner access rules when configured.

Live count observed on 2026-09-10:

- L1 workspace snapshot: 29 entities total.
- Breakdown: `chat=24`, `kb=5`, `notebook=0`, `quiz=0`, `book=0`, `partner=0`, `cowriter=0`.
- L2 facts: 0.
- L3 propositions: 0 in visible synthesis slots. The backend also has a `preferences` L3 slot, but no preference markdown exists right now.
- L2 KB trace backlog: 132 trace events.

## 23. Memory Data Flow

Memory has two L1 mechanisms:

- L1 workspace snapshot: live adapters scan real workspace state and return one entity per artifact. This powers `/api/v1/memory/snapshot/{surface}` and the Memory hub's "entities tracked" number.
- L1 trace log: append-only JSONL event files under `data/memory/trace/<surface>/<YYYY-MM-DD>.jsonl`. In this workspace, only KB trace files currently exist.

L1 to L2:

- The workbench calls `POST /api/v1/memory/runs/start` or legacy `POST /api/v1/memory/doc/{layer}/{key}/update`.
- L2 update reads current snapshot entities for one surface.
- It skips already-seen entity refs using sidecar metadata.
- It chunks entity content, calls the selected/default LLM, parses facts, validates refs, and writes `data/memory/L2/<surface>.md`.

L2 to L3:

- L3 update reads L2 docs.
- It creates cross-surface synthesis for `recent`, `profile`, or `scope`.
- `preferences` is excluded from normal consolidation; it is written by the chat `write_memory` tool only.

Chat/model flow:

- If the user manually selects memory in chat, the frontend sends `memory_references`.
- Backend turn runtime reads `MemoryStore.read_l3_concat()` and injects L3 markdown into the chat system prompt as a `memory` block.
- If any L3 file has content, `read_memory` can auto-mount as a tool, allowing the model to fetch L3 during chat.
- `write_memory` is always part of the normal auto-mounted tool floor and can write explicit preferences.

## 24. What Each Memory Level Actually Contains

L1 contains current workspace entities and trace events.

- `chat`: one entity per chat session, including message content for consolidation.
- `notebook`: one entity per notebook record.
- `quiz`: recorded quiz/question-bank attempts, one aggregate entity per LearningStore mastery/progress path, and one entity per saved exam attempt.
- `kb`: one entity per registered knowledge base, plus trace events for KB queries.
- `book`: one entity per book/reading material manifest.
- `partner`: one entity per partner conversation session.
- `cowriter`: one entity per co-writer document.

L2 contains per-surface markdown facts:

- Files are expected at `data/memory/L2/chat.md`, `notebook.md`, `quiz.md`, `kb.md`, `book.md`, `partner.md`, and `cowriter.md`.
- In the current workspace these files do not exist, so L2 is empty.

L3 contains cross-surface markdown synthesis:

- Backend slots: `recent`, `profile`, `scope`, `preferences`.
- The Memory hub/graph only counts and displays `recent`, `profile`, and `scope`.
- Chat `read_l3_concat()` reads all four backend slots, including `preferences`.
- In the current workspace no L3 markdown files exist; only `data/memory/L3/recent.meta.json` exists.

## 25. Does Memory Actually Personalize the AI?

Yes, but only when there is actual L3 content or when the user attaches memory context.

Current status in this workspace:

- Automatic durable memory personalization is effectively not active, because L3 markdown content is empty.
- Manual memory selection in chat is wired, but selecting any memory artifact causes the backend to inject the full L3 concat. With empty L3 docs, that contributes no useful personalization.
- The `read_memory` tool is gated by `user_has_memory()`, which checks for non-empty L3 content. With empty L3, the model should not get `read_memory`.
- The `write_memory` tool can still save explicit preferences if the model calls it after the user clearly states a preference.

Important limitation:

- Memory is not magic continuous learning. L1 can show 29 entities, but the model is not personalized from those entities until L2/L3 have been built or the user explicitly attaches other context.

## 26. What Information Can Reach External Model Providers?

Local until used:

- Stored chats, memory files, learning state, exams, settings, and KB files live locally under `data/` unless a feature sends them to a model/provider.

Can reach the active LLM provider:

- Chat prompt, conversation history summary/context, selected KB seed, selected memory L3 text, persona, attached source manifest, file-extracted text, question-bank context, book context, and tool results.
- Memory consolidator prompts and L1/L2 chunks when Memory Update/Audit/Dedup runs.
- Exam generation prompts and source/RAG context when generating an exam.
- Starter-suggestion prompts containing L3 memory plus recent activity labels.
- Voice/STT/TTS audio or text if configured to use a cloud voice provider.
- Embedding inputs and RAG indexing/query text if the active embedding/RAG provider is cloud.

Provider boundary:

- `LLMSelection` only carries `profile_id` and `model_id`; secrets stay server-side in the model catalog.
- The actual destination depends on configured providers, for example OpenAI-compatible cloud endpoints, Ollama/local endpoints, Krutrim/custom providers, embedding providers, LightRAG/PageIndex, and voice providers.
- Ollama/local providers keep requests on the configured local endpoint; cloud providers receive the prompt/context sent for that operation.

## 27. What a Blind User Should Expect

On the Memory page:

- The headline counts are status counters, not proof that the tutor is personalized.
- "L1 29 entities" means Smart Tutor can see 24 chat sessions and 5 knowledge bases in the workspace snapshot.
- "L2 0 facts" means no per-surface facts have been built.
- "L3 0 propositions" means no cross-surface learner profile/recent/scope synthesis has been built.

On chat:

- If memory is empty, the tutor should behave like normal chat plus whatever current context the user selects.
- Selecting "Memory" in the composer is wired, but right now there is no meaningful L3 content to inject.
- Bottom starter suggestions can use recent activity labels and L3 memory. With empty L3, they rely mainly on recent activity.

On Practice/Exam/Mastery:

- Practice and exam attempts can update question/progress stores.
- They now appear as `quiz` L1 snapshot evidence when stored in question rows, LearningStore, or exam attempts.
- They do not automatically mean L2/L3 memory has been consolidated; the user still needs a Memory Run or an approved background run to build derived docs.
- Mastery state remains authoritative in LearningStore; Memory is a derived/context layer over it.

## 28. Current L1/L2/L3 Health

Current health is mixed:

- L1 workspace snapshot: healthy and reachable. API calls returned current entities for all seven surfaces.
- L1 trace: partially populated. KB trace logs exist; other trace surfaces are empty.
- L2: empty. No L2 markdown docs exist.
- L3: empty. No L3 markdown docs exist.
- Memory settings API: healthy. `/api/v1/memory/settings` returns budgets, chunking, reference, merge, and dedup settings.
- Memory overview API: healthy. `/api/v1/memory/overview` returned all 11 docs with zero entries.
- Memory graph: wired, but graph value is limited because L2/L3 are empty and the frontend excludes `preferences`.

Verification performed:

- `GET /api/v1/memory/snapshot/{surface}` for all surfaces.
- `GET /api/v1/memory/overview`.
- `GET /api/v1/memory/settings`.
- Targeted tests: `189 passed in 1.46s` for memory services, memory resolver, and session turn-runtime extraction.

## 29. Memory Problems Requiring Repair

1. L2/L3 are not built yet.
   - User impact: memory page shows tracked entities, but the tutor has no durable learner profile/scope/recent synthesis.
   - Repair type: operational/documented workflow plus better no-op visibility.

2. L1 wording is confusing.
   - The UI and graph say "raw traces", but the main count comes from live workspace snapshot entities.
   - Repair type: copy/docs fix first; code only if product wants different naming.

3. Memory picker is narrower than backend.
   - Frontend offers `summary` and `profile`.
   - Backend accepts `recent`, `profile`, `scope`, `preferences`, and `summary`, then injects full L3 concat if any are selected.
   - Repair type: align UI labels/options with backend behavior.

4. Empty memory can feel like a broken Run. RESOLVED FOR RUN STATUS on 2026-09-11.
   - Update can legitimately produce no edits.
   - Current behavior: Memory Run now renders `No new input`, `No memory document`, and `No changes` outcomes in the run timeline.
   - Remaining limitation: L2/L3 can still be empty until the user intentionally runs memory consolidation.

5. Invalid/unavailable selected model can be softened. RESOLVED on 2026-09-11.
   - Current behavior: explicit invalid `{profile_id, model_id}` selections fail the run with an error instead of silently falling back.
   - Valid explicit selections emit a `model_selected` event with the resolved provider/model.
   - Total LLM failure now ends the run as an error instead of returning an empty model response.

6. L3 `preferences` is hidden from some UI counts.
   - Backend reads it for chat and exposes it in docs, but Memory hub/graph visible totals exclude it.
   - Repair type: decide whether to show it as a fourth L3 slot or clearly label it as hidden/private preference memory.

7. Exam learning update swallows exceptions. RESOLVED on 2026-09-11.
   - `ExamService.submit_exam()` now logs progress-write errors without changing exam scoring behavior.

## 30. Recommended Memory Repair Order

1. DONE 2026-09-11: Add visible no-op/error status to Memory Run. Invalid selected models now error instead of fallback.
2. Clarify L1 UI copy: "workspace snapshot" versus "trace events".
3. DONE 2026-09-11: Add a safe memory-smoke test that uses disposable storage and mocked LLM to prove LearningStore evidence can flow L1 to L2 to L3.
4. Align MemoryPicker options with backend L3 slots, or change backend injection to honor selected slots.
5. DONE 2026-09-11: Add provider/model run events for valid selected models and hard failure for invalid selected models.
6. Decide how to expose `preferences` in L3 UI.
7. DONE 2026-09-11: Add logging around swallowed exam progress-write failures.
8. After those are stable, run an intentional one-time memory build over real data only with user approval, because it can mutate memory docs and spend model tokens.

## 31. 2026-09-11 Memory Run Implementation Update

Implemented:

- Shared memory-run LLM activation now treats `None` as default-model behavior and treats an explicit invalid selection as a `ValueError`.
- Memory update/audit/dedup no longer log-and-ignore invalid explicit selections.
- Valid explicit selections emit `model_selected` with provider/model details.
- Memory LLM calls still fall back from streaming to non-streaming when possible, but if both fail the run now records an error.
- Memory Run UI now displays selected model, no-new-input, no-doc, and no-change outcomes.

Verified:

- `.\.venv\Scripts\python.exe -m pytest tests\services\memory\test_modes.py -q`: 11 passed.
- `.\.venv\Scripts\python.exe -m pytest tests\services\memory tests\api\test_memory_resolver.py tests\services\session\test_turn_runtime.py -q`: 194 passed.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint -- components/memory/MemoryRunPanel.tsx`: passed with 0 errors and 129 existing warnings.

Still open:

- L2/L3 markdown docs are still not automatically built from real user data.
- MemoryPicker labels/options are still narrower than backend L3 slots.
- Background/Foreground remain architectural/product concepts, not named implemented product features.

## 32. 2026-09-11 Learning Activity Memory Bridge

Implemented:

- The existing `quiz` L1 surface now reads three evidence sources:
  - question/notebook quiz rows from chat history,
  - LearningStore mastery/progress aggregates,
  - saved exam attempt results.
- LearningStore remains authoritative; Memory reads a compact aggregate entity per path instead of copying the learning database.
- Exam attempt records remain authoritative under the exam store; Memory reads one compact entity per submitted attempt.
- Exam learning-progress write failures are now logged instead of swallowed silently.

Verified:

- `.\.venv\Scripts\python.exe -m pytest tests\services\memory\test_snapshot_adapters.py -q`: 9 passed.
- `.\.venv\Scripts\python.exe -m pytest tests\services\memory\test_modes.py -q`: 12 passed.
- `.\.venv\Scripts\python.exe -m pytest tests\services\memory tests\api\test_memory_resolver.py tests\services\session\test_turn_runtime.py -q`: 197 passed.
- `.\.venv\Scripts\python.exe -m pytest smarttutor\learning\tests tests\exam\test_exam_learning_integration.py tests\api\test_notebook_router.py::test_quiz_results_update_learning_progress -q`: 298 passed.
- `.\.venv\Scripts\python.exe -m pytest tests\exam\test_exam_learning_integration.py -q`: 1 passed.

Final learning-memory flow now verified in disposable tests:

Learning activity -> LearningStore -> `quiz` L1 snapshot entity -> L2 `quiz.md` consolidation -> L3 `scope.md` synthesis -> chat-readable L3 memory path.

Known limitations:

- No real user memory docs were generated.
- Background auto-consolidation was not added.
- A one-off incorrect answer is still controlled by LLM/prompt behavior during consolidation; tests verify the pipeline, not every possible provider output.
