# Smart Tutor Complete Feature And Behavior Inventory

Audit date: 2026-08-29  
Workspace: `D:\project\deep-tutor`  
Scope: documentation-only inspection of the existing Smart Tutor codebase, current status documentation, and previously recorded local verification results.  
Code changes in this pass: none.

## Status Legend

- ✅ VERIFIED WORKING: inspected and backed by a real local test or direct runtime status.
- 🟢 IMPLEMENTED — NOT FULLY VERIFIED: code and UI/API are present, but this audit did not complete a full browser/runtime workflow.
- 🟡 PARTIAL: meaningful implementation exists, but gaps remain in behavior, integration, polish, or verification.
- ⚠️ CONFIGURATION REQUIRED: feature depends on credentials, local binaries, models, external services, or user setup.
- ❌ BROKEN: inspected or tested and known not to work in the current machine state.
- ⬜ NOT IMPLEMENTED: requested/product-expected feature is not present as a complete feature.
- 🚫 INTENTIONALLY NOT USED: explicitly out of scope or intentionally avoided.

## Feature Matrix

| Feature | UI Exists | Backend Exists | Uses RAG | Uses Student Data | Interactive | Tested | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Local launcher `start-smart-tutor.bat` | Yes | Yes | No | No | Yes | Yes | ✅ VERIFIED WORKING |
| Project-root `.env` as primary config | No | Ignored by design | No | No | No | Yes | 🚫 INTENTIONALLY NOT USED |
| Runtime settings under `data/user/settings` | Yes | Yes | No | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Main sidebar navigation | Yes | N/A | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Tutor chat page | Yes | Yes | Optional | Yes | Yes | Partly | 🟡 PARTIAL |
| Chat recents/session list | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Session rename/delete | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Unified WebSocket chat | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| OpenAI chat provider | Yes | Yes | Optional | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Ollama/local chat provider | Yes | Yes | Optional | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Separate embedding provider selection | Yes | Yes | Yes | No | Yes | Yes | ✅ VERIFIED WORKING |
| Ollama `nomic-embed-text` embeddings | Yes | Yes | Yes | No | Yes | Yes | ✅ VERIFIED WORKING |
| Model selector/chat model picker | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Settings model catalog editor | Yes | Yes | No | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Settings service diagnostics/tests | Yes | Yes | No | No | Yes | Yes | ✅ VERIFIED WORKING |
| Knowledge Base / My Library page | Yes | Yes | Yes | Yes | Yes | Partly | 🟡 PARTIAL |
| LlamaIndex KB creation | Yes | Yes | Yes | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| PDF document ingestion | Yes | Yes | Yes | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Duplicate document upload handling | Yes | Yes | Yes | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| RAG search with citations/sources | Yes | Yes | Yes | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Knowledge indexing progress stream | Yes | Yes | Yes | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| File preview/download/delete in KB | Yes | Yes | Yes | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Linked folder sync | Yes | Yes | Yes | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Obsidian/MarginNote/IMA connectors | Yes | Yes | Optional | Yes | Yes | Not live tested | ⚠️ CONFIGURATION REQUIRED |
| GraphRAG pipeline | Yes | Yes | Yes | Yes | Yes | Not live tested | ⚠️ CONFIGURATION REQUIRED |
| LightRAG local/server pipeline | Yes | Yes | Yes | Yes | Yes | Not live tested | ⚠️ CONFIGURATION REQUIRED |
| PageIndex pipeline | Yes | Yes | Yes | Yes | Yes | Not live tested | ⚠️ CONFIGURATION REQUIRED |
| Chat quick action: Teach me | Yes | Via chat | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Chat quick action: Explain | Yes | Via chat | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Chat quick action: Simplify | Yes | Via chat | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Chat quick action: Summarize | Yes | Via chat | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Chat quick action: Quiz | Yes | Via chat/deep_question | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Chat quick action: Test | Yes | Via chat | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Chat quick action: Practice | Yes | Via chat | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Chat quick action: Revise | Yes | Via chat/mastery_path | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Chat quick action: Weak topics | Yes | Via chat/memory/progress | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Quiz generation configuration | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Quiz mimic paper mode | Yes | Yes | Optional | Yes | Yes | Not live tested | 🟡 PARTIAL |
| Interactive quiz viewer | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| AI quiz judging | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Question bank/categories | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Revision/mastery dashboard | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Mastery progress map | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Mastery activity feed/events | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Persistent learning progress storage | Yes | Yes | No | Yes | Yes | Tests exist | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Book generator/reader | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Book block editing/regeneration | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Book quiz attempts/weak chapters | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Notebook library | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Save chat/quiz content to notebook | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Memory overview/workbench | Yes | Yes | No | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Memory graph/L1/L2/L3 pages | Yes | Yes | No | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Personas page/API | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Partners and subagents | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟡 PARTIAL |
| Playground/capability tester | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Deep solve capability | Yes | Yes | Optional | Yes | Yes | Not live tested | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Deep research capability | Yes | Yes | Optional | Yes | Yes | Not live tested | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Visualize capability | Yes | Yes | Optional | Yes | Yes | Not live tested | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Math animator capability | Yes | Yes | Optional | Yes | Yes | Not live tested | ⚠️ CONFIGURATION REQUIRED |
| Co-writer | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Reading materials/annotations | Yes | Yes | Optional | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| STT microphone button | Yes | Yes | No | Yes | Yes | API tested only | 🟡 PARTIAL |
| Global faster-whisper STT | Settings/API | Yes | No | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| OpenAI Whisper global STT | Settings/API | Yes | No | Yes | Yes | Yes | ❌ BROKEN |
| whisper-timestamped global STT | Settings/API | Yes | No | Yes | Yes | Yes | ❌ BROKEN |
| Edge TTS global speech output | Settings/API | Yes | No | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Windows System.Speech TTS | Settings/API | Yes | No | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Piper TTS | Settings/API | Yes | No | Yes | Yes | Discovery tested | ⚠️ CONFIGURATION REQUIRED |
| pyttsx3 TTS | Settings/API | Yes | No | Yes | Yes | Yes | ❌ BROKEN |
| gTTS TTS | Settings/API | Yes | No | Yes | Yes | Yes | ⚠️ CONFIGURATION REQUIRED |
| OpenAI TTS | Settings/API | Yes | No | Yes | Yes | Yes | ✅ VERIFIED WORKING |
| Azure Speech | No | No | No | No | No | N/A | 🚫 INTENTIONALLY NOT USED |
| Accessibility/NVDA support | Partial | N/A | No | No | Yes | Not manually tested | 🟡 PARTIAL |
| Auth/profile/admin users | Yes | Yes | No | Yes | Yes | Code-inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |

Features audited: 72

## Main Navigation Inventory

Primary sidebar:

- My Library: `/knowledge`. Knowledge-base management, document ingestion, provider settings, file operations, progress.
- Tutor: `/home`. Main chat/tutoring surface. Locked when the user lacks LLM access.
- Practice: `/space/questions`. Question bank and saved quiz/question workflow.
- Revision: `/space/learning`. Mastery-path dashboard with maps, activity, redo, delete, skip pending question, and continue in chat.
- Progress: `/memory`. Memory/progress workbench, including layered memory pages.

Secondary sidebar:

- Settings: `/settings`. Hub for appearance, network, models, knowledge parsing, chat, partners/agents, and memory.
- Recents: visible on chat-enabled layout, supports session selection, rename, and delete.

Other workspace routes found:

- `/book`: generated book/reader workspace.
- `/co-writer` and `/co-writer/[docId]`: document editing and automarking workspace.
- `/partners`, `/partners/new`, `/partners/[partnerId]`: partner/agent companion management.
- `/playground`: capability tester for chat, quiz generation, mastery path, deep research, solve, visualize, and related capabilities.
- `/whisper`: legacy/experimental voice route exists in the workspace tree.
- `/admin/users`: admin user management.

## Settings Inventory

Settings hub categories:

- Appearance: theme and interface language.
- Network: ports, browser API base, and CORS.
- Models:
  - LLM
  - Embedding
  - Search
  - Text-to-Speech
  - Speech-to-Text
  - Image Generation
  - Video Generation
- Knowledge Base:
  - Document parsing engine.
  - MinerU, Docling, Tika, parser testing, model download jobs.
- Chat:
  - Tools.
  - Capabilities.
  - Starting points.
  - Attachments.
- Partners & Agents:
  - Claude Code.
  - Codex.
  - Gemini CLI.
  - Kimi CLI.
  - opencode.
  - MiMo Code.
- Memory:
  - chunking, budget, deduplication, references, and memory run behavior.

Settings persistence:

- Most runtime model/provider state lives in `data/user/settings/model_catalog.json`.
- UI/interface state lives in `data/user/settings/interface.json`.
- Network and attachment settings live in `data/user/settings/system.json`.
- Capability/memory settings use `data/user/settings/main.yaml` and related YAML/JSON settings.
- Project-root `.env` is intentionally not the source of truth for this app.

## Tutor Chat Inventory

The Tutor page contains:

- Main composer.
- Model selector.
- Capability selector.
- Knowledge-base selector.
- Agent selector.
- Attachment handling.
- Voice recorder integration.
- Starter suggestions from `/api/v1/dashboard/suggestions`.
- Session viewer panel with artifacts, previews, quiz follow-ups, and visualization follow-up prompts.
- Streamed tool/capability trace panels.

Learning quick actions:

- Teach me: step-by-step grounded tutoring from the selected material.
- Explain: passage/main-idea explanation with document grounding.
- Simplify: beginner-friendly explanation with jargon definitions and a small example.
- Summarize: core ideas, important details, and review targets.
- Quiz: short quiz from selected material, with source explanations.
- Test: one-at-a-time conceptual/application questions.
- Practice: worked example followed by adaptive practice.
- Revise: focused review plan and first review prompt.
- Weak topics: infer weak topics from session, saved progress, and selected material.

Status:

- The UI and backend plumbing are present.
- LLM provider calls were verified for OpenAI and Ollama/local.
- Full browser journey from uploaded material to cited answer was not retested in this documentation-only pass, so the overall chat workflow remains partial rather than fully verified here.

## Knowledge, Document, RAG, And Vector Flow

Verified RAG path:

- LlamaIndex provider.
- PDF ingestion.
- Ollama `nomic-embed-text` embedding model.
- 768-dimensional local embeddings.
- Queryable RAG service.
- Retrieved source snippets and citations.
- Duplicate upload detection immediately after KB creation.

Implemented but not fully verified:

- GraphRAG.
- LightRAG.
- LightRAG server.
- PageIndex.
- IMA.
- Obsidian and MarginNote-style connected sources.
- Linked-folder sync.
- Knowledge file preview, move, delete, and reindex operations.

ASCII flow:

```text
User document
  |
  v
Knowledge UI upload / create KB
  |
  v
FastAPI knowledge router
  |
  v
KnowledgeBaseInitializer / DocumentAdder
  |
  v
Raw file copy + metadata + duplicate hash check
  |
  v
Selected RAG provider
  |
  v
Parser -> chunks -> embeddings -> provider index/vector store
  |
  v
RAGService.search
  |
  v
Tutor answer with retrieved sources
```

## Quiz, Test, Exam, Practice, And Question Bank

Quiz generation:

- Capability: `deep_question`.
- UI configuration supports custom and mimic-paper modes.
- Custom mode supports count, difficulty, selected question types, and per-type ratio distribution.
- Question types: multiple choice, concept/true-false, fill in the blank, short answer, essay/written, coding.
- Streamed quiz question extraction exists, so questions can render before the final result event.

Quiz viewer:

- Question navigation.
- Per-question answer state.
- Auto-grading for multiple choice, concept, and fill-in-blank.
- Open-ended answer handling for short answer, essay, and coding.
- Image answers.
- AI judging over typed and image answers.
- Reference answer/judgment tabs.
- Reset answer.
- Bookmark.
- Category filing.
- Follow-up chat tab per quiz question.
- Results recorded to the session only when a valid quiz turn id exists.

Question bank:

- Backend supports upsert, list, lookup by question, delete, category bulk actions, category create/delete, and stats.
- Frontend question-bank components exist for scope rail, toolbar, category manager, cards, and selection.

Exam status:

- The app has quiz/test/practice behavior and question-bank persistence.
- A separate full exam mode with timed exam session, scoring report, attempt history, and student-facing exam dashboard was not found as a complete standalone product surface.
- Status: ⬜ NOT IMPLEMENTED for full exam mode; 🟡 PARTIAL for test/practice behavior through chat and quiz.

ASCII flow:

```text
Tutor Quiz mode / Playground
  |
  v
QuizConfigPanel
  |
  v
Unified WS -> deep_question capability
  |
  v
Question pipeline emits quiz_question_emitted events
  |
  v
QuizViewer renders cards
  |
  v
Learner answers -> local grading / AI judge
  |
  v
Session quiz results + question notebook entry
  |
  v
Question bank, categories, follow-up chat
```

## Revision, Mastery, Weak Topics, And Progress

Revision page:

- Lists mastery paths with objective count and average mastery.
- Shows selected path map.
- Shows next action.
- Shows due reviews.
- Shows recent activity.
- Supports continuing the path in Tutor chat.
- Supports redo/reset, delete, and skip pending question.

Backend:

- `/api/v1/learning/progress`
- `/api/v1/learning/progress/{book_id}`
- `/api/v1/learning/progress/{book_id}/map`
- `/api/v1/learning/progress/{book_id}/objectives/{kp_id}`
- `/api/v1/learning/progress/{book_id}/events`
- `/api/v1/learning/progress/{book_id}/sessions`
- `/api/v1/learning/progress/{book_id}/init-modules`
- `/api/v1/learning/progress/{book_id}/import-from-book`
- `/api/v1/learning/progress/{book_id}/skip-question`
- `/api/v1/learning/progress/{book_id}/redo`
- `/api/v1/learning/progress/{book_id}/generate-from-notebook`

Known behavior:

- Progress state is durable and modelled with modules, objectives, mastery levels, attempts, due reviews, pending questions, and events.
- The Revision dashboard is intended to follow a tutoring session live by polling events after the current revision.
- Full live end-to-end mastery session was not retested in this pass.

ASCII flow:

```text
Tutor in Revision/mastery mode
  |
  v
mastery_path capability
  |
  v
LearningService + LearningStore
  |
  v
Modules, knowledge points, attempts, mastery levels, review schedule
  |
  v
Mastery events with path revision
  |
  v
/space/learning dashboard
  |
  v
Map + activity + next step + continue in chat
```

## Books And Reader

Book workspace:

- Lists books.
- Creates books from selected sources, notebooks, and question entries.
- Handles proposal, spine, compile-page, resume, rebuild, and delete operations.
- Shows generation progress timeline.
- Reads pages and blocks.
- Supports block update, insert, delete, move, change type, regenerate, supplement, and deep dive.
- Tracks visited pages, bookmarks, quiz attempts, weak chapters, score, and current page.
- Links page-specific chat sessions.
- Supports learning captures.
- Exports generated books.

Block types found:

- text
- callout
- quiz
- user note
- figure
- interactive
- animation
- code
- timeline
- flash cards
- deep dive
- section
- concept graph

Status:

- Implementation is substantial.
- This pass did not run a full book generation cycle, so the product status is partial.

## Memory And Notebooks

Memory surfaces:

- Memory overview.
- Memory graph.
- L1 memory.
- L2 memory.
- L3 memory.
- Resolve entry.
- Snapshot and trace routes.
- Memory settings.
- Memory run panel/workbench.

Memory backend:

- overview
- resolve entry
- backup
- document read/update/delete/reset
- run start/get/cancel/undo/list/events
- audit/dedup/apply
- trace and snapshot endpoints

Notebook features:

- Notebook health.
- List/statistics.
- Create/read/update/delete.
- Add record.
- Add record with generated summary.
- Update/delete/copy/move records.
- Export notebook as plain text.
- Save-to-notebook modal can create the first notebook without leaving the dialog.
- Records can be saved from chat/quiz contexts.

Status:

- Memory and notebook code is present and feature-rich.
- Full user-level memory correctness was not retested in this documentation-only pass.

ASCII flow:

```text
Chat / Quiz / Book content
  |
  v
Save to Notebook or memory run
  |
  v
Notebook router / Memory router
  |
  v
data/user storage
  |
  v
Notebook library, Memory workbench, Progress sidebar
  |
  v
Future Tutor context and weak-topic review
```

## Voice, STT, And TTS

Voice endpoints:

- `GET /api/v1/voice/capabilities`
- `POST /api/v1/voice/stt`
- `POST /api/v1/voice/tts`

Selected STT:

- Provider: `faster_whisper`.
- Adapter: global subprocess adapter.
- Global executable: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\python.exe`.
- Package owner: global Python site-packages.
- Model: `tiny`.
- Live result: API transcription returned `Smart Tudor Local Voice Recording Test.`

Selected TTS:

- Provider: `edge_tts`.
- Adapter: global subprocess adapter.
- Global executable: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\Scripts\edge-tts.EXE`.
- Package owner: global Python site-packages.
- Live result: API returned `audio/mpeg`; generated MP3 played successfully in the earlier audit.

Other engines:

- Windows System.Speech: available and tested through the adapter.
- OpenAI TTS: available and tested through the existing configured OpenAI provider.
- gTTS: available and tested, but requires internet.
- Piper: package installed globally, but no voice model pair was found.
- pyttsx3: installed globally, but synthesis failed.
- OpenAI Whisper and whisper-timestamped: installed globally, but blocked by the current Numba/NumPy mismatch.
- Azure Speech: intentionally not used.

Voice fallback behavior:

- Smart Tutor uses configured providers from the runtime model catalog.
- The global adapter reports capabilities through `/api/v1/voice/capabilities`.
- If the configured global executable/package is unavailable, STT/TTS requests fail with provider errors rather than silently installing duplicates into `.venv`.
- The project should keep using global Whisper/TTS components when technically safe and practical.

ASCII flow:

```text
Browser microphone / uploaded audio
  |
  v
/api/v1/voice/stt
  |
  v
Configured STT provider
  |
  v
Global Python subprocess imports faster_whisper
  |
  v
Transcript returned to composer
```

```text
Chat answer text
  |
  v
/api/v1/voice/tts
  |
  v
Configured TTS provider
  |
  v
Global edge-tts executable or alternate provider
  |
  v
Audio bytes returned to browser
  |
  v
Playback control/autoplay setting
```

Known voice limitation:

- The prior test used generated local WAV audio, not a physical microphone recording from the user's browser. Browser microphone permission and hardware recording still need manual verification on the user's machine.

## AI Providers, Tools, Capabilities, And Agents

Built-in capabilities:

- `chat`
- `deep_solve`
- `deep_question`
- `deep_research`
- `math_animator`
- `visualize`
- `mastery_path`
- `immersive_reading`

User-toggleable tools:

- `brainstorm`
- `web_search`
- `paper_search`
- `reason`

Context-gated or capability-mounted tools include:

- `rag`
- `kb_files`
- `read_source`
- `read_memory`
- `write_memory`
- `read_skill`
- `load_tools`
- `exec`
- `code_execution`
- `list_notebook`
- `write_note`
- `web_fetch`
- `github`
- `cron`
- `ask_user`
- mastery-path tools
- reading tools
- setup tools
- subagent tools
- partner memory tools
- image/video generation tools

Subagents/partners:

- Backend supports detection, options, sync, partner connections, message calls, settings, sessions, branching, and WebSocket chat.
- Settings pages exist for local CLI agents such as Claude Code, Codex, Gemini, Kimi, opencode, and MiMo.
- Status is partial because external agent binaries/accounts and real partner workflows were not fully tested here.

## Reading Materials And Annotations

Reading backend supports:

- supported formats
- materials list/create/read/delete
- unit text
- raw material download
- annotations list/upsert/delete
- export

Reader components include PDF rendering and text/selection behavior.

Status:

- Implemented, but full browser reading and annotation workflow was not retested in this pass.

## Accessibility Inventory

Observed accessibility-supporting implementation:

- Icon buttons include labels/titles in many places.
- Sidebar locked items expose disabled state and tooltip.
- Chat voice controls include recorder/playback status from the previous voice pass.
- Layout includes keyboard-clickable buttons and links across major surfaces.
- Language support exists for English/Chinese UI copy in many areas.

Gaps:

- No completed NVDA/manual screen-reader pass is recorded for every page.
- Physical microphone flow with browser permission was not manually verified.
- Some complex surfaces, especially quiz, memory graph, book editor, and capability trace panels, need keyboard and screen-reader walkthroughs.

Status: 🟡 PARTIAL.

## User Journeys

### A. Upload textbook, ask for grounded explanation

```text
Open My Library
  -> Create/select KB
  -> Upload textbook/PDF
  -> Watch indexing progress
  -> Open Tutor
  -> Select KB
  -> Ask "Explain this chapter"
  -> Chat calls RAG
  -> Answer includes sources
```

Status: ✅ VERIFIED WORKING for backend ingestion/RAG; 🟡 PARTIAL for full browser UI journey.

### B. Ask Tutor to teach a topic step by step

```text
Open Tutor
  -> Select model
  -> Optionally select KB/document/agent
  -> Click Teach me
  -> Chat sends guided prompt
  -> Tutor explains, checks understanding, and cites selected material when available
```

Status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

### C. Generate and answer a quiz

```text
Open Tutor
  -> Select Quiz capability or quick action
  -> Configure count, difficulty, type mix, or mimic paper
  -> Generate quiz
  -> QuizViewer streams/render questions
  -> Learner answers
  -> Auto-grade or AI judge
  -> Save result to session/question bank
  -> Open follow-up chat for a question
```

Status: 🟡 PARTIAL because UI/API are implemented but full generation-to-persistence was not live tested in this pass.

### D. Revise weak topics

```text
Open Revision
  -> Select mastery path
  -> Inspect map, due reviews, and next action
  -> Continue in Tutor
  -> Tutor asks/grades mastery questions
  -> LearningStore records attempts and events
  -> Revision map updates
```

Status: 🟡 PARTIAL.

### E. Use voice input and spoken answer

```text
Open Tutor
  -> Press microphone
  -> Browser records audio
  -> /api/v1/voice/stt sends audio to global faster-whisper
  -> Transcript appears in composer
  -> Send message
  -> Chat answer arrives
  -> /api/v1/voice/tts sends text to Edge TTS
  -> Browser plays returned MP3
```

Status: ✅ VERIFIED WORKING for STT/TTS APIs and generated-audio playback; 🟡 PARTIAL for physical browser microphone.

### F. Save learning content and reuse it later

```text
Read/chat/quiz
  -> Save useful answer/question to Notebook
  -> Optional generated summary
  -> Organize records
  -> Use notebook records to generate a mastery path or book source
  -> Tutor/revision reads the saved context
```

Status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

# Current Product Readiness

## Genuinely Working

- Local backend/frontend launch was verified.
- OpenAI chat provider is configured and tested without exposing the key in docs.
- Ollama/local model discovery and local LLM diagnostic work.
- Embeddings are separated from chat provider selection.
- Ollama `nomic-embed-text` embeddings work with 768 dimensions.
- LlamaIndex PDF ingestion and RAG search work.
- Duplicate upload detection works immediately after KB creation.
- Voice diagnostics endpoint works.
- Global faster-whisper STT works through Smart Tutor.
- Global Edge TTS works through Smart Tutor and returns playable audio.
- Windows System.Speech and OpenAI TTS were tested as available paths.

## Implemented Not Fully Verified

- Main Tutor chat UI and session management.
- Model selector and provider settings UI.
- Knowledge file operations beyond the verified PDF path.
- Quiz generation UI, interactive quiz viewer, AI judge, bookmarks, category filing, and follow-up tabs.
- Question bank.
- Notebook CRUD and save-to-notebook workflow.
- Personas.
- Co-writer.
- Reading materials and annotations.
- Playground/capability tester.
- Deep solve, deep research, visualize, and several built-in tools.

## Partially Implemented

- Full student-facing practice/test/revision workflows.
- Full browser upload-to-grounded-answer journey.
- Book generation and reader as a production learning path.
- Memory/progress as an understandable student dashboard.
- Accessibility and NVDA coverage.
- Physical browser microphone recording.
- Partners/subagents as an end-user learning feature.

## Broken

- Global OpenAI Whisper CLI path is blocked by the current global Numba/NumPy mismatch.
- Global whisper-timestamped is blocked by the same Whisper dependency problem.
- pyttsx3 imports, but real synthesis failed on this machine.

## Missing

- Standalone full exam mode with timer, attempt lifecycle, scoring report, and review workflow.
- Fully verified physical microphone browser test.
- Piper voice-model setup.
- A simple student-facing "what is ready" screen that hides developer/debug complexity.
- End-to-end automated browser tests for the full learn-from-document path.

## Intentionally Not Used

- Azure Speech.
- Project-root `.env` as the primary runtime settings mechanism.
- Automatic duplicate Whisper/TTS installation into Smart Tutor `.venv`.

## Next Steps Ranked

1. Verify and harden the complete browser journey: My Library upload -> indexing progress -> Tutor selects KB -> grounded answer with citations.
2. Turn quiz/test/practice/revision into one polished student workflow with clear entry points, persisted attempts, weak-topic recommendations, and progress reporting.
3. Add a standalone exam mode only after the quiz/practice path is stable.
4. Finish the browser microphone verification and expose clearer voice capability selection/status in Settings.
5. Run an accessibility pass with keyboard-only navigation and NVDA across Tutor, QuizViewer, Revision, My Library, and Settings.
6. Decide whether Piper should be supported locally by documenting or installing voice model files, not by silently downloading packages into `.venv`.
7. Reduce student-facing clutter by separating learner UI from developer/admin diagnostics.

# Student-Facing Learning Experience Audit

This section extends the technical audit above with a stricter student-experience audit. It distinguishes code that exists from behavior that has been manually or end-to-end verified.

## Student Experience Matrix

| Feature | UI | Interactive | Uses Uploaded Material | Uses RAG | Evaluates Student | Saves Result | Updates Progress | NVDA Reviewed | Status |
|---|---|---|---|---|---|---|---|---|---|
| Teach | Tutor quick action | Yes, via chat follow-up | Yes, if attachment/source selected | Optional, if KB selected and model calls RAG | Prompt asks to check understanding; no automatic grading | Chat session saved | No direct progress update verified | NOT VERIFIED | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Explain | Tutor quick action and reader quote action | Yes | Yes, if selected text/attachment/source selected | Optional | No | Chat session saved | No | NOT VERIFIED | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Simplify | Tutor quick action | Yes | Yes, if selected source/attachment exists | Optional | No | Chat session saved | No | NOT VERIFIED | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Summarize | Tutor quick action | Yes | Yes, if selected source/attachment exists | Optional | No | Chat session saved | No | NOT VERIFIED | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Quiz | Tutor quick action, Quiz capability config, QuizViewer | Yes | Yes, if attachment/KB/config uses it | Optional | Yes for some types; AI judge available | Session quiz results and question-bank entries | Session quiz results saved; mastery progress not automatically verified | NOT VERIFIED | 🟡 PARTIAL |
| Test | Tutor quick action only | Chat-interactive | Yes, if selected material exists | Optional | Prompt asks model to track misses; no dedicated test engine found | Chat session saved | No dedicated progress update verified | NOT VERIFIED | 🟡 PARTIAL |
| Practice | Tutor quick action plus question-bank page | Chat-interactive | Yes, if selected material exists | Optional | Prompt asks adaptive practice; no dedicated practice scorer verified | Chat session/question bank depending workflow | No automatic progress update verified | NOT VERIFIED | 🟡 PARTIAL |
| Revise | Tutor quick action and Revision page | Yes | Yes, if selected material/path exists | Optional | Mastery path can evaluate through mastery tools | Learning progress storage exists | Yes in mastery path, not verified for quick action | NOT VERIFIED | 🟡 PARTIAL |
| Weak Topics | Tutor quick action, book progress, memory/progress surfaces | Chat-interactive | Optional | Optional | No direct evaluation; reads inferred state if available | Chat session saved | Weak-chapter/progress fields exist; update path not fully verified | NOT VERIFIED | 🟡 PARTIAL |
| Progress | Sidebar Progress/Memory and Revision dashboard | Yes | Indirect | No | Displays stored attempts/events | Durable stores exist | Yes, for mastery/book/session data | NOT VERIFIED | 🟡 PARTIAL |
| Voice | Mic button and TTS playback path | Yes | No | No | No | Transcript becomes chat message when sent | No | NOT VERIFIED | 🟡 PARTIAL |
| Exam/Call Exam | Mimic Exam in Playground/Quiz mimic mode; no full exam app | Partial | Uploaded exam paper in mimic mode | Not the main mechanism | No full exam grading lifecycle found | Quiz artifacts/session may be saved | No exam progress verified | NOT VERIFIED | ⬜ NOT IMPLEMENTED |

## What Happens When I Click It?

| Button | Immediate Action | Backend Action | Data Used | Result | Persistent Data | Status |
|---|---|---|---|---|---|---|
| Teach me | Sends a fixed prompt from the Tutor quick-action list | Unified WS routes to chat unless another capability is selected | Current message, selected KBs, selected agent, open reader/source manifest, attachments, conversation history | Chat answer intended to teach step by step and ask/check understanding | User/assistant messages and attachment metadata in session DB | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Explain | Sends a fixed explanation prompt; reader selection can also create an "Explain this passage" prompt | Unified WS chat/capability runtime | Selected text if invoked from reader, current sources, KBs, attachments, history | Explanation, optionally grounded if source/RAG is used | Chat messages | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Simplify | Sends a fixed simplification prompt | Unified WS chat runtime | Selected material, attachments, KBs, history | Beginner-level explanation with jargon definitions and example requested | Chat messages | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Summarize | Sends a fixed summarization prompt | Unified WS chat runtime | Selected material, attachments, KBs, history | Summary with core ideas/details/review targets requested | Chat messages | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Quiz | Sends a quiz prompt when used as quick action; capability mode uses `deep_question` config | Unified WS -> `deep_question`; quiz events rendered by QuizViewer | Topic/config, optional uploaded PDF, KBs, attachments, history depending mode | Structured quiz cards when capability output is valid | Session messages, quiz results, question-bank entries when submitted with turn id | 🟡 PARTIAL |
| Test | Sends a fixed test prompt | Unified WS chat runtime | Selected material, KBs, attachments, history, model knowledge | One-question-at-a-time behavior is requested from model, not enforced by a test UI | Chat messages | 🟡 PARTIAL |
| Practice | Sends a fixed practice prompt | Unified WS chat runtime | Selected material, KBs, attachments, history, possible progress if model/tool reads it | Worked example and adaptive practice are requested from model | Chat messages; question bank only in separate workflows | 🟡 PARTIAL |
| Revise | Sends a fixed revision-plan prompt | Unified WS chat runtime; true mastery paths use `mastery_path` capability when selected | Selected material, saved progress if available, history, KBs | Review plan and first prompt requested; mastery mode can run gated tutoring | Chat messages; mastery progress only in mastery-path flow | 🟡 PARTIAL |
| Weak topics | Sends a fixed weak-topic prompt | Unified WS chat runtime | Session, saved progress, selected material if accessible | Model explanation/recommendations | Chat messages; weak-topic records not directly updated by this button | 🟡 PARTIAL |
| Suggest what to explore next | Calls starter suggestion refresh button under composer | `/api/v1/dashboard/suggestions/refresh` -> suggestions service | Recent traces, L3 memory/profile, KB/chat/book/notebook/question labels | Three clickable suggested prompts, or idle/no-material state | Cached suggestions JSON | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |

## Quick Actions: Actual Behavior

All nine fixed learning quick actions are defined in `web/app/(workspace)/home/[[...sessionId]]/page.tsx` as label/prompt pairs. They do not each have a dedicated backend route. Pressing one sends its prompt through the same chat send path as a typed student message. The backend path is the unified WebSocket/session runtime, which builds context from conversation history, selected KBs, attachments, source inventory, notebook/history/book/question-bank references, persona, memory references, and the selected capability.

### Teach Me

- UI location: Tutor page, learning quick action row.
- Frontend component: `web/app/(workspace)/home/[[...sessionId]]/page.tsx` renders `LearningActionGrid`.
- Backend route/API: unified chat WebSocket/session runtime, not a dedicated Teach route.
- Service/function called: chat turn runtime -> `ChatOrchestrator`/chat capability; RAG only if selected KB and model/tool loop calls `rag`.
- Prompt used: "Teach me the selected material step by step. Use the open Reader document and selected Library sources as the grounding, check my understanding as we go, and cite the document when you use it."
- Input/context used: selected material, source manifest, selected KBs, selected agent, attachments, conversation history, persona, optional memory references.
- Attached files: usable when attached; document text is extracted and persisted in attachment metadata.
- Knowledge Base/RAG: available but not forced by the button.
- Conversation history: yes, bounded and summarized by `ContextBuilder`.
- Student progress/history: not directly used unless selected via memory/progress or mastery path context.
- Output format: normal chat answer.
- One-shot or interactive: starts as one chat turn; follow-up makes it interactive.
- State maintained: chat session state is maintained.
- Results saved: chat messages and attachment metadata are saved.
- Progress updated: NOT VERIFIED.
- Weak topics updated: NOT VERIFIED.
- Automated tests: no Teach-specific E2E test found.
- Real E2E test: NOT VERIFIED.
- Current status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

Actual conclusion: Teach me is a strong guided prompt, not a separate deterministic teaching engine. Progressive teaching, examples, checking understanding, and citations are requested from the model; they are not enforced by a dedicated Teach state machine.

### Explain

- UI location: Tutor quick action; reader selection path also inserts an "Explain this passage" prompt.
- Frontend component: Tutor page plus reader selection integration.
- Backend route/API: unified chat WebSocket/session runtime.
- Service/function called: chat capability, with optional source/RAG tools.
- Prompt used: "Explain the current passage or main idea from the selected material. Ground the explanation in the open document or selected Library source and cite the evidence you use."
- Input/context used: selected/open material, attachment text, source manifest, selected KBs, conversation history.
- Attached files: yes if attached.
- Knowledge Base/RAG: optional; not forced.
- Conversation history: yes.
- Student history/progress: not inherently.
- Output format: normal chat answer.
- Interaction: one turn plus follow-ups.
- State/results: chat messages saved.
- Progress/weak topics: NOT VERIFIED.
- Tests/E2E: NOT VERIFIED.
- Current status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

### Simplify

- UI location: Tutor quick action.
- Frontend component: Tutor page learning actions.
- Backend route/API: unified chat WebSocket/session runtime.
- Prompt used: "Simplify the selected material for a beginner. Keep the answer grounded in the document, define any jargon, and include a tiny example."
- Source use: attachment/source/KB context is available when selected.
- Reading-level change: requested in prompt, not enforced by a separate simplification service.
- Fact preservation: requested indirectly through grounding; NOT VERIFIED by tests.
- Output: normal chat answer.
- Progress/weak topics: no direct update found.
- Tests/E2E: NOT VERIFIED.
- Status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

### Summarize

- UI location: Tutor quick action.
- Frontend component: Tutor page learning actions.
- Backend route/API: unified chat WebSocket/session runtime.
- Prompt used: "Summarize the selected material. Separate the core ideas, important details, and anything I should review again, using citations from the document where available."
- Summary types: asks for core ideas, details, review points; no separate short/detailed/formulas/definitions selector found in this quick action.
- Source-grounding: available if selected material/KB/attachment is available and used.
- Output: normal chat answer.
- Progress/weak topics: no direct update found.
- Tests/E2E: NOT VERIFIED.
- Status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

### Quiz

- UI location: Tutor quick action and `deep_question` capability configuration panel.
- Frontend components: `QuizConfigPanel`, `QuizViewer`, `QuizFollowupTabBody`, `FollowupChatComposer`.
- Backend route/API: unified WS for capability execution; quiz judge WebSocket `/api/v1/quiz/question/judge`; session quiz results route `/api/v1/sessions/{session_id}/quiz-results`; question notebook routes.
- Service/function called: `DeepQuestionCapability`, question pipeline/coordinator, quiz judge, question notebook persistence.
- Prompt/instruction: quick action prompt asks to create a short quiz and wait for answers; capability config sends structured quiz settings.
- Input/context: topic/config, optional uploaded PDF for mimic mode, selected KBs, attachments, history, model knowledge.
- Attached files: yes in chat/capability path; mimic mode supports uploaded exam PDF.
- RAG: optional via selected KB/tool path; mimic exam mode parses a paper into templates, not a full permanent RAG exam engine.
- Conversation history: yes.
- Student progress/history: quiz answers can be saved to session/question bank; mastery-progress connection not fully verified.
- Output format: structured question cards in QuizViewer when quiz metadata/events are present.
- Interaction: interactive.
- State maintained: per-question answer state, turn-scoped persisted entries, follow-up sessions.
- Results saved: yes, when session id and turn id are available.
- Progress updated: session quiz results are saved; mastery progress not automatically verified.
- Weak topics updated: book progress has weak chapters, but quiz-to-weak-topic path is NOT VERIFIED.
- Automated tests: unit tests exist around quiz/session/learning storage; no full browser E2E recorded here.
- Real E2E test: NOT VERIFIED in this pass.
- Status: 🟡 PARTIAL.

### Test

- UI location: Tutor quick action named Test.
- Frontend component: Tutor page learning actions.
- Backend route/API: unified chat WebSocket/session runtime.
- Dedicated test/exam service: no standalone Test route or test engine found.
- Prompt used: "Test my understanding of the selected material with a mix of conceptual and application questions. Ask one question at a time and track what I miss."
- Evaluation: model-prompted only unless the user is in Quiz/Mastery flows.
- State/results/progress/weak topics: chat state saved; dedicated test progress not found.
- E2E: NOT VERIFIED.
- Status: 🟡 PARTIAL.

### Practice

- UI location: Tutor quick action; Practice sidebar page points to question bank.
- Frontend component: Tutor learning actions and question-bank UI components.
- Backend route/API: unified chat runtime; question notebook APIs for saved questions.
- Prompt used: "Give me targeted practice on the selected material. Start with one worked example, then give me a similar problem to try, and adapt based on my answer."
- Adaptivity: requested from model, not enforced by a dedicated practice scheduler in the quick action.
- Previous mistakes: available only if surfaced through memory/question-bank/progress context; automatic use is NOT VERIFIED.
- Accuracy/progress: not directly updated by quick action.
- E2E: NOT VERIFIED.
- Status: 🟡 PARTIAL.

### Revise

- UI location: Tutor quick action; Revision sidebar page.
- Frontend component: Tutor learning actions and `/space/learning` mastery dashboard.
- Backend route/API: quick action uses unified chat runtime; mastery dashboard uses `/api/v1/learning/progress/...`.
- Prompt used: "Help me revise this material. Build a focused review plan from the selected sources, prioritize weak topics, and start with the first review prompt."
- True revision engine: `mastery_path` capability and learning APIs exist.
- Uploaded material/KB: available if selected.
- Previous mistakes/weak topics: can be part of progress/memory context; quick-action use is NOT VERIFIED.
- Flashcards: book block type exists, but this quick action does not expose a flashcard generator control.
- Progress update: verified in learning service tests, not live E2E from quick action.
- Status: 🟡 PARTIAL.

### Weak Topics

- UI location: Tutor quick action, Progress/Memory sidebar, Book progress fields, Revision dashboard.
- Backend: learning models store attempts/errors/mastery; book progress stores `weak_chapters`; memory stores can hold learner profile/scope.
- Prompt used: "Identify my weak topics from this session, my saved progress, and the selected material. Explain the evidence for each weak topic and recommend what to practice next."
- Calculation: no single dedicated weak-topic scoring service was found for all quiz/test/practice/exam mistakes.
- Quiz mistakes: session quiz results and question notebook entries exist; automatic weak-topic aggregation is NOT VERIFIED.
- Exam/practice mistakes: no full exam/practice lifecycle found.
- Recovery after improvement: mastery levels/review scheduler support improvement, but weak-topic recovery is NOT VERIFIED.
- Revise/Practice use: requested by prompt; deterministic use NOT VERIFIED.
- Status: 🟡 PARTIAL.

### Suggest What To Explore Next

- UI location: beneath the home composer as starter suggestions.
- Frontend component: `StarterSuggestions`.
- Backend routes: `/api/v1/dashboard/suggestions` and `/api/v1/dashboard/suggestions/refresh`.
- Service/function: `smarttutor.services.suggestions`.
- Prompt/instruction: backend asks the LLM for exactly three trace-grounded proposals.
- Input/context: recent activity traces across chat, quiz, notebooks, KBs, books, co-writer, partners, plus L3 learner memory/profile.
- Attachments/RAG: not direct RAG; uses labels/traces/cache, not document retrieval.
- Conversation history/student history: yes, through recent traces and memory.
- Output: three clickable labels with hidden full prompts.
- State: suggestions cached in workspace suggestions JSON.
- E2E: NOT VERIFIED.
- Status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

## Quiz/Exam Control Matrix

| Control | Quiz | Test/Exam | Keyboard Accessible | Screen Reader Labeled | Verified |
|---|---|---|---|---|---|
| Radio buttons | No native radio control found; choice options are custom buttons | Not found | Likely clickable/focusable if buttons; native arrow-key radio behavior absent | Button text visible; native radio group semantics absent | NOT VERIFIED |
| Checkboxes | Category/selection controls exist elsewhere; quiz multiple-select not confirmed | Not found | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| Text answer | Yes for fill-in/free-text types | No standalone exam UI | Standard inputs/textareas likely keyboard reachable | Labels not fully audited | NOT VERIFIED |
| Next | Yes, previous/next question navigation buttons | Not found | Button controls | aria-label/title present in QuizViewer for Previous; Next likely similar | NOT VERIFIED |
| Previous | Yes | Not found | Button controls | `aria-label`/title observed for Previous | Code-inspected only |
| Skip | No general QuizViewer skip button found; Revision has skip pending question | Not found | Revision button exists | NOT VERIFIED | NOT VERIFIED |
| Review | Reference/Judgment review area exists | No full exam review found | Toggle/buttons exist | NOT VERIFIED | NOT VERIFIED |
| Submit | Per-question submit exists | No full exam submit found | Button control | NOT VERIFIED | NOT VERIFIED |
| Timer | Not found | Not found | N/A | N/A | ⬜ NOT IMPLEMENTED |
| Results | Quiz completion and per-question correctness exist; full score report not confirmed | Not found | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| Retry | Per-question reset exists; mastery redo exists | Not found | Button control | NOT VERIFIED | NOT VERIFIED |

## Quiz Deep UI Audit

Question types actually represented in code:

- Single-choice MCQ: supported as `choice`.
- Multiple-choice: same `choice` bucket; multi-select checkbox behavior was not verified.
- Multiple-select: NOT IMPLEMENTED/NOT VERIFIED as a distinct type.
- True/false: supported as `concept` with true/false resolution.
- Fill-in-the-blank: supported as `fill_in_blank`.
- Short answer: supported as `short_answer`.
- Long answer: represented as `written` / essay.
- Numerical answer: no distinct numerical type found.
- Matching: no matching type found.
- Coding: supported as `coding`.

Answer controls:

- Choice/concept questions use selectable UI controls in `QuizViewer`; native HTML radio-group semantics were not verified and no native radio inputs were identified in the inspected portion.
- Fill-in/free-text questions use typed answer state.
- Image answer upload is supported for AI judging.
- Category filing/bookmark/follow-up buttons exist.
- Keyboard accessibility is plausible for button/input controls but NOT VERIFIED by manual keyboard or NVDA testing.

Quiz interaction:

- One question at a time: yes, `idx` state selects the active card.
- Multiple questions on screen: no, active viewer focuses on one question with chips for navigation.
- Question numbering/progress: yes, completed/total and numbered chips exist.
- Next/Previous: yes.
- Skip: not as a general QuizViewer control.
- Change answer: reset/change behavior exists.
- Review answers: reference/judgment review section exists.
- Submit: per-question submit exists.
- Confirmation before final submission: not found for quiz.

Evaluation:

- Immediate/per-question evaluation exists after submission for auto-gradable types.
- Correct/incorrect feedback exists for auto-gradable types.
- Explanation/reference is available from generated question data.
- AI judgment is available for richer typed/image answers.
- Full score/percentage/marks result page was not confirmed.
- Mistakes are saved as quiz results/question entries when session/turn identity exists.
- Weak topics and global progress updates from quiz mistakes are NOT VERIFIED.

Source grounding:

- Quiz can use attached files and selected KB context when routed through the unified chat/capability context.
- Permanent KB RAG is available but not guaranteed by the quick action itself.
- Mimic mode can parse an uploaded exam paper/PDF into templates.
- The model can still use general model knowledge unless prompts/tool constraints force grounding; no hard safeguard was verified that prevents unrelated questions in every quiz path.

## Test / Exam / Call Exam Audit

Observed exam-related implementation:

- `Mimic Exam` appears in the Playground deep-question tester.
- Backend question routes include WebSocket endpoints for mimic exam paper question generation.
- Question tooling includes exam-paper parsing/extraction and mimic mode.
- `DeepQuestionCapability` supports mimic mode from uploaded PDF or parsed exam directory.

What was not found:

- No standalone student Exam page.
- No full "Call Exam" route/component/service found as a complete exam product.
- No duration/timer lifecycle found.
- No exam sections/navigation/review/unanswered dashboard found.
- No final marks/percentage/pass-fail exam report found.
- No saved exam attempt history found.
- No dedicated exam progress/weak-topic integration verified.

Exam creation capabilities:

- Subject/chapter selection: NOT FOUND as a full exam form.
- Uploaded exam PDF: supported for mimic mode.
- Permanent KB selection: available in general capability/chat context, not confirmed as exam form control.
- Number of questions/difficulty/types: supported in QuizConfigPanel custom mode.
- Marks/duration/sections: NOT IMPLEMENTED in observed UI.

Exam grounding:

- Mimic mode grounds style/templates in an uploaded exam paper.
- RAG-grounded exam generation from the student's permanent KB is NOT VERIFIED.
- Safeguard against unrelated questions: NOT VERIFIED.

Status: ⬜ NOT IMPLEMENTED for a full exam product; 🟡 PARTIAL for mimic-exam quiz generation.

## Practice Deep Audit

Practice is currently a chat quick action plus the separate question-bank/practice surface. The quick action asks for a worked example and an adaptive follow-up problem. No dedicated practice session engine was found that deterministically tracks accuracy, repeats missed questions, adapts difficulty, and writes weak-topic/progress records across attempts.

Actual state:

- Generates questions: model can, by prompt; Quiz/Question Bank can generate/store questions in adjacent flows.
- Uses KB/RAG: optional, not forced.
- Uses previous mistakes: possible through memory/question-bank/progress context; NOT VERIFIED.
- Adapts difficulty: prompt-requested; NOT VERIFIED as a scheduler.
- Tracks accuracy: quiz/session stores can track results; practice quick action does not have a verified accuracy tracker.
- Repeats missed questions: NOT VERIFIED.
- Provides explanations: prompt-requested; quiz explanations exist.
- Tracks progress/weak topics: NOT VERIFIED for the Practice button.

Status: 🟡 PARTIAL.

## Revision Deep Audit

Revision has two overlapping meanings:

- The Revise quick action: a chat prompt that asks for a focused review plan.
- The Revision dashboard/mastery path: a real persisted learning system.

Implemented mastery behavior:

- Progress summaries.
- Mastery map.
- Objective reports.
- Activity events.
- Pending question handling.
- Redo/reset.
- Skip pending question.
- Import/generate modules from books/notebooks.
- Continue path in Tutor chat.

Not fully verified:

- Starting a complete mastery path from a student's uploaded PDF in the browser.
- Quick Revise automatically creating flashcards.
- Quick Revise automatically updating progress.
- Quick Revise deterministically using weak-topic data.

Status: 🟡 PARTIAL.

## Weak Topics And Progress Storage

Storage found:

- Chat/session data: SQLite session store with messages, attachments, metadata, quiz result route, and branch-aware history.
- Learning/mastery data: `LearningStore` persists modules, knowledge points, mastery levels, attempts, pending questions, error records, review state, sessions, and events.
- Book progress: `Progress` includes current page, visited pages, bookmarked pages, quiz attempts, weak chapters, score, and updated timestamp.
- Memory: L1/L2/L3 memory docs, traces, snapshots, audits, dedup, and updates.
- Question bank: question entries, categories, stats, user answers, bookmarks, images, and AI judgments.
- Notebook: notebook records and generated summaries.

What actually creates weak topics:

- Book progress has `weak_chapters`.
- Learning service records attempts/errors and mastery, which can imply weaknesses.
- Memory L3 scope/profile can store learner uncertainty.
- A single global weak-topic algorithm across quiz, test, practice, exam, confidence, accuracy, and recovery was not verified.

Progress fields covered:

- Quizzes: session quiz results and question-bank entries exist.
- Tests/exams: no dedicated persisted exam model found.
- Practice: no dedicated practice lifecycle found.
- Revision: mastery path progress exists.
- Questions answered/correct/incorrect: quiz and learning attempt models exist.
- Scores/accuracy: book score and mastery percentages exist; full cross-product score model not verified.
- Chapters/subjects: book/progress modules and chapters exist.
- Dates/sessions/history: timestamps, sessions, and events exist.

Status: 🟡 PARTIAL.

## Personas Audit

Personas are Markdown behavior presets stored under `data/user/workspace/personas/<name>/PERSONA.md`; admin-authored read-only presets can also be exposed to non-admin users. They are style/behavior guidance, not separate tools, capabilities, permissions, or model configurations.

| Persona | System Prompt / Instructions | Model | Tools | RAG/KB Access | Behavior Difference | Tests | Manual E2E |
|---|---|---|---|---|---|---|---|
| teacher | Socratic tutor; lead with a question, small steps, concrete examples, diagnose rather than lecture, end with follow-up/summary | Uses selected chat model | Same turn tools as chat | Same selected KB/source access as chat | Should change tone and pedagogy through injected context | NOT FOUND | NOT VERIFIED |
| research-assistant | Cite or qualify claims, distinguish evidence/opinion, surface methodology, map landscape, flag gaps | Uses selected chat model | Same turn tools as chat | Same selected KB/source access as chat | Should produce more rigorous/citation-oriented answers | NOT FOUND | NOT VERIFIED |
| peer | Curious study partner, think out loud, push back, admit uncertainty, short conversational style | Uses selected chat model | Same turn tools as chat | Same selected KB/source access as chat | Should feel collaborative rather than authoritative | NOT FOUND | NOT VERIFIED |

Actual injection path:

```text
PersonaSelector / @space persona
  |
  v
payload.persona
  |
  v
turn_runtime loads PERSONA.md
  |
  v
UnifiedContext.persona_context
  |
  v
chat/capability prompt context
```

Status: 🟢 IMPLEMENTED — NOT FULLY VERIFIED.

## Attachment vs Permanent Knowledge

Temporary chat attachment:

- UI: chat composer attachment control/drag-paste path.
- Storage: original bytes are persisted through the attachment store under the chat session; message rows store attachment metadata and URL, not full base64 after processing.
- Extraction: supported document formats are extracted by `smarttutor.utils.document_extractor`; extracted text is saved in attachment metadata.
- Lifetime: tied to the chat/session storage. It can be reused by later turns in the same session/branch through the source inventory, but it is not automatically a permanent KB document.
- Removed attachment: if removed before send, it is not part of that turn. Removal behavior after send is not fully audited.
- Chat ends: session persists unless deleted; attachment metadata/URLs are session artifacts, not permanent library documents.
- RAG: not indexed into the permanent vector store by default.

Permanent Knowledge Base document:

- UI: My Library / Knowledge page.
- Storage: copied into `data/knowledge_bases/<kb>/raw/...` with KB metadata/config.
- Processing: parser -> chunks -> embedding -> selected RAG provider index/vector storage.
- Lifetime: persists until the KB/file is deleted.
- Multiple questions: selected KB can be reused across multiple chat turns without re-uploading.
- Deletion: knowledge router has file and KB delete endpoints.
- Duplicate detection: initial KB creation and upload track file hashes and skip duplicate re-uploads.
- Re-embedding: duplicate upload skips staging and avoids re-embedding in the verified LlamaIndex path.

## Complete RAG User Journey Verification

| Step | Actual Behavior | Verification |
|---|---|---|
| Student uploads PDF to KB | Knowledge upload/create routes and UI exist | ✅ VERIFIED WORKING for audited Science PDF |
| File accepted | PDF accepted by validator/upload path | ✅ VERIFIED WORKING |
| Parsing | LlamaIndex provider uses document loader/parser | ✅ VERIFIED WORKING for audited PDF |
| Text extraction | Retrieved text included PDF header/instructions | ✅ VERIFIED WORKING |
| Chunking | Provider chunks documents during indexing | ✅ VERIFIED WORKING at outcome level; chunk parameters not deeply audited |
| Embedding | Ollama `nomic-embed-text` used | ✅ VERIFIED WORKING |
| Vector/index storage | Provider version/index folders created and queryable | ✅ VERIFIED WORKING |
| Processing complete | KB reported ready/searchable | ✅ VERIFIED WORKING |
| Student asks question | RAG service can search; full browser chat path not retested | 🟡 PARTIAL |
| Retrieval | `RAGService.search` returned 3 sources | ✅ VERIFIED WORKING |
| Context sent to model | RAG tool returns content/sources to chat loop; exact prompt payload not live inspected | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |
| Answer | OpenAI chat works; grounded final browser answer not retested | 🟡 PARTIAL |
| Citations/source references | RAG tool exposes sources; UI renders sources/traces | 🟢 IMPLEMENTED — NOT FULLY VERIFIED |

## Multi-Question Behavior

Expected implementation behavior:

- Permanent KB selection is carried in the chat/session request state.
- RAG retrieval is per question/turn when the model/tool loop calls `rag`.
- The document is not re-embedded for every question; it uses the existing KB index.
- Re-chunking/re-indexing happens during KB creation/upload/reindex, not normal question answering.
- Re-uploading the same permanent document is skipped by duplicate detection in the verified path.
- Temporary attachments can remain available in the session's source inventory, but they are not permanent vector-index records.

Verification:

- Reusing the same KB over Question 1 -> Question 4 in a real browser session is NOT VERIFIED.
- Avoiding re-embedding during normal multi-question chat is inferred from architecture and verified duplicate upload behavior, but the exact multi-turn browser run is NOT VERIFIED.

Status: 🟡 PARTIAL.

## Voice User Journey

| Step | Actual Behavior | Verification |
|---|---|---|
| Record voice in browser | Microphone hook/UI exists | NOT VERIFIED with physical browser microphone |
| Browser uploads audio | `/api/v1/voice/stt` accepts uploaded audio | ✅ VERIFIED WORKING with generated WAV |
| STT provider | Active provider is global faster-whisper | ✅ VERIFIED WORKING |
| Transcript | API returned transcript text | ✅ VERIFIED WORKING |
| Transcript to chat | Composer integration exists | NOT VERIFIED end-to-end in browser |
| AI response | OpenAI/Ollama chat providers work | ✅ VERIFIED WORKING provider-level |
| TTS request | `/api/v1/voice/tts` exists | ✅ VERIFIED WORKING |
| Audio playback | Generated Edge TTS MP3 playback passed in prior audit | ✅ VERIFIED WORKING |

TTS providers:

- Edge TTS: ✅ VERIFIED WORKING.
- Windows System.Speech: ✅ VERIFIED WORKING.
- OpenAI TTS: ✅ VERIFIED WORKING.
- gTTS: ⚠️ CONFIGURATION REQUIRED because it needs internet.
- Piper: ⚠️ CONFIGURATION REQUIRED because no `.onnx` plus `.onnx.json` voice model pair was found.
- pyttsx3: ❌ BROKEN for synthesis on this machine.
- Azure Speech: 🚫 INTENTIONALLY NOT USED.

STT providers:

- global faster-whisper: ✅ VERIFIED WORKING and selected.
- openai-whisper: ❌ BROKEN due global Numba/NumPy mismatch.
- whisper-timestamped: ❌ BROKEN due same dependency issue.
- ctranslate2: installed dependency used by faster-whisper, not a direct Smart Tutor STT provider.

## Accessibility: Student UI

CODE IMPLEMENTED:

- Many controls are buttons/inputs with visible labels, titles, or `aria-label`.
- Model selector uses `aria-live` for model status.
- Sidebar locked items expose disabled state and tooltip text.
- Quiz Previous button has `aria-label`/title.
- Starter suggestions use real buttons.
- Voice status announcements were added in the prior voice work.

ACTUALLY TESTED WITH NVDA:

- NOT VERIFIED for Quiz.
- NOT VERIFIED for Test/Exam.
- NOT VERIFIED for Practice.
- NOT VERIFIED for Revision.
- NOT VERIFIED for Voice.
- NOT VERIFIED for Settings.

Specific gaps:

- Native radio-group semantics for Quiz MCQ were not verified.
- Checkbox/multiple-select quiz behavior was not verified.
- Timer announcements are not applicable because full exam timer was not found.
- Question-change announcement is NOT VERIFIED.
- Score/result announcement is NOT VERIFIED.
- Submit confirmation announcement is NOT VERIFIED.

Status: 🟡 PARTIAL.

## Normal Student Settings vs Developer Configuration

Student/user-facing settings that make sense:

- Language/interface.
- Theme.
- Active chat model when multiple allowed models are exposed.
- Voice input/output provider and voice selection.
- Basic attachment limits/status.
- Default response language.
- Knowledge Base selection/management for their own documents.
- Memory privacy/clear controls.

Internal/developer/admin configuration:

- Provider base URLs.
- API keys and OAuth provider wiring.
- Embedding dimensions.
- GraphRAG/LightRAG/PageIndex internals.
- MinerU/Docling/Tika executable/model-download settings.
- CORS and port configuration.
- MCP/server catalog.
- Agent CLI runtime flags.
- Tool/capability low-level parameters.

Current assessment:

- Settings are powerful but complex for a normal student.
- Non-admin users are protected from raw catalog secrets by the settings API.
- A simpler student settings layer is still missing.

## Model Selection Audit

Actual behavior:

- Chat model picker calls `/api/v1/settings/llm-options`.
- Admins can refresh local Ollama LLM profiles.
- Model options are grouped by provider and local/cloud category.
- OpenAI and Ollama/local models are supported.
- Embedding is configured through separate Settings -> Models -> Embedding.
- `nomic-embed-text` is documented and verified as the active embedding model.
- Because chat picker consumes LLM options rather than embedding catalog options, embedding models should not appear as normal chat models.

Verification:

- OpenAI provider works: YES — VERIFIED.
- Ollama provider/model discovery works: YES — VERIFIED.
- Embedding separation works: YES — VERIFIED at provider/settings level.
- Visual browser check that `nomic-embed-text` is absent from the chat model dropdown: NOT VERIFIED in this pass.

## Status Buckets

## VERIFIED WORKING

- Local launcher and server/frontend startup.
- OpenAI provider.
- Ollama provider discovery and embedding.
- LlamaIndex PDF ingestion/RAG.
- Duplicate permanent document detection.
- Voice STT through global faster-whisper API path.
- Voice TTS through Edge TTS API path.
- Windows System.Speech and OpenAI TTS provider tests.
- Settings provider diagnostics.

## IMPLEMENTED — NOT FULLY VERIFIED

- Teach, Explain, Simplify, Summarize quick actions.
- Suggest what to explore next.
- Persona injection.
- Model picker behavior.
- Notebook and question-bank UI/API.
- QuizViewer interactions beyond inspected code.
- Reading/annotation surfaces.
- Co-writer, Playground, Deep Solve, Deep Research, Visualize.

## PARTIAL

- Quiz as a complete student assessment workflow.
- Test/Practice/Revise quick actions as deterministic learning engines.
- Weak-topic calculation and recovery.
- Progress across all learning modes.
- Full RAG browser journey.
- Full voice browser journey.
- Accessibility/NVDA readiness.

## BROKEN

- openai-whisper global path.
- whisper-timestamped global path.
- pyttsx3 synthesis.

## NOT IMPLEMENTED

- Full standalone Exam/Call Exam product.
- Exam timer, marks, sections, review dashboard, final result report, saved exam history.
- Distinct numerical/matching/multiple-select quiz types as verified first-class controls.
- Simple student-only settings mode.

## CONFIGURATION REQUIRED

- Piper voice models.
- gTTS internet access.
- GraphRAG/LightRAG/PageIndex/IMA/Obsidian/MarginNote advanced connectors.
- Math animator dependencies/rendering stack.
- External/local subagent binaries.

## NOT YET END-TO-END TESTED

- Student uploads PDF in browser, creates KB, asks four follow-up questions, sees citations each time.
- Student generates quiz, answers every type, sees score, saves mistakes, and sees Progress/Weak Topics update.
- Student starts Practice and has difficulty adapt based on previous mistakes.
- Student starts Revision from a KB/book/notebook and sees mastery progress update live.
- Student records real microphone audio in browser, sends chat, hears TTS playback.
- NVDA pass across Tutor, Quiz, Revision, Practice, Progress, Voice, and Settings.

# Student Experience Gaps

## P0 — Critical

- Full browser RAG journey is not yet verified end to end.
- Quiz does not yet prove a complete student assessment lifecycle from generation to scoring to progress/weak-topic updates.
- Full Test/Exam product is missing.
- Weak Topics are not verified as a computed, recoverable, cross-workflow student model.
- Progress is split across session quiz results, learning mastery, book progress, memory, and question bank without a verified unified student view.

## P1 — Important

- Practice is currently mostly prompt-driven rather than a verified adaptive practice engine.
- Revise quick action is prompt-driven; real mastery path exists but is not verified from the quick-action journey.
- Physical browser microphone recording is not verified.
- NVDA accessibility is not actually tested for student-critical flows.
- Quiz controls need semantic verification, especially radio/checkbox behavior and screen-reader labels.
- Settings are too complex for normal students and mix user-facing choices with admin/developer configuration.

## P2 — Nice To Have

- Piper local voice support needs voice model files.
- Suggestion quality needs real learner-history testing.
- Personas need manual A/B response tests.
- Model picker should be visually verified to exclude embedding-only models.
- Exam mimic mode should be renamed or clearly separated from a real exam product.

## Recommended Next Implementation Plan

1. Verify and harden the permanent KB RAG browser journey with one PDF and four follow-up questions.
2. Finish Quiz as a complete student workflow: native accessible controls, submit/review/results, scoring, saved attempts, and clear explanations.
3. Connect quiz mistakes to Progress and Weak Topics.
4. Build or explicitly defer a standalone Test/Exam workflow with timer, marks, sections, navigation, submit confirmation, result report, and history.
5. Turn Practice into a real adaptive loop that reads previous mistakes, tracks accuracy, repeats misses, and updates progress.
6. Connect Weak Topics back into Practice and Revise.
7. Verify Revision/mastery path creation from permanent KB/book/notebook sources in a browser.
8. Complete physical browser voice recording and playback testing.
9. Run NVDA and keyboard-only tests for Tutor, Quiz, Revision, Practice, Progress, Voice, and Settings.
10. Simplify Settings into student-facing and admin/developer-facing modes.

# Smart Tutor — Current Reality

| Question | Answer |
|---|---|
| 1. Can a student upload a textbook? | YES — VERIFIED for permanent KB PDF path; browser UI journey PARTIAL |
| 2. Is it parsed? | YES — VERIFIED for audited PDF |
| 3. Is it chunked? | YES — VERIFIED at provider outcome level |
| 4. Is it embedded? | YES — VERIFIED with Ollama `nomic-embed-text` |
| 5. Is it stored in the vector/index database? | YES — VERIFIED for LlamaIndex index path |
| 6. Can the student ask multiple questions about it? | YES — IMPLEMENTED, NOT VERIFIED end to end |
| 7. Does duplicate upload avoid re-embedding? | YES — VERIFIED for audited duplicate PDF |
| 8. Can the document be permanently stored? | YES — VERIFIED through KB storage |
| 9. Does Teach me work? | YES — IMPLEMENTED, NOT VERIFIED |
| 10. Does Explain work? | YES — IMPLEMENTED, NOT VERIFIED |
| 11. Does Simplify work? | YES — IMPLEMENTED, NOT VERIFIED |
| 12. Does Summarize work? | YES — IMPLEMENTED, NOT VERIFIED |
| 13. Does Quiz work? | PARTIAL |
| 14. Does Quiz have radio buttons/checkboxes/etc.? | PARTIAL; custom choice controls and text/image answers exist, native radio/checkbox behavior NOT VERIFIED |
| 15. Does Quiz evaluate answers? | PARTIAL; auto-grading for some types and AI judge exist |
| 16. Does Test/Exam work? | NOT IMPLEMENTED as a full exam product |
| 17. Does Test/Exam have proper exam controls? | NOT IMPLEMENTED |
| 18. Does Practice work? | PARTIAL |
| 19. Does Revise work? | PARTIAL |
| 20. Does Weak Topics work? | PARTIAL |
| 21. Does Progress work? | PARTIAL |
| 22. Does Teacher persona work? | YES — IMPLEMENTED, NOT VERIFIED |
| 23. Does Researcher persona work? | YES — IMPLEMENTED, NOT VERIFIED |
| 24. Does OpenAI work? | YES — VERIFIED |
| 25. Does Ollama work? | YES — VERIFIED |
| 26. Does model selection work? | YES — IMPLEMENTED, NOT VERIFIED; provider diagnostics verified |
| 27. Does global faster-whisper work? | YES — VERIFIED |
| 28. Does TTS work? | YES — VERIFIED for Edge TTS, Windows System.Speech, and OpenAI TTS |
| 29. Does Record Voice work in a real browser? | NOT VERIFIED |
| 30. Is NVDA accessibility actually tested? | NOT VERIFIED |

Student-experience features audited in this extension: 30 current-reality questions, 13 matrix features, 11 quiz/exam controls, 10 major click actions, 3 personas, and 7 major workflow areas.

# Smart Tutor — Student Learning Loop Implementation Update

Date: 2026-08-29

## Implemented

- Quiz submissions now update the existing mastery/progress system through `POST /api/v1/sessions/{session_id}/quiz-results`.
- The same submitted answers still write the chat `[Quiz Performance]` summary and upsert the question notebook entries.
- Quiz answers now carry `concentration` and `knowledge_context` from the generated question payload into the backend, so progress objectives and weak-topic labels can use the actual topic when available.
- The backend creates a safe, session-derived learning path id and records quiz-derived objectives in the existing `LearningStore` SQLite aggregate.
- Incorrect submitted answers create existing `ErrorRecord` weak-topic records through `LearningService.record_quiz_attempt`.
- Later correct evidence on the same topic can graduate active/retrying weak-topic records once the topic reaches the existing mastery gate.
- Quiz choice and true/false controls now use native radio inputs inside fieldsets, while preserving the existing visual treatment.
- Fill-in-the-blank and free-text quiz answers now have explicit labels.
- Quiz navigation chips now expose step/current-state labels for assistive technology.

## Reused Existing Infrastructure

- Session history remains in the existing SQLite session store.
- Question history remains in the existing question notebook store.
- Mastery/progress remains in `smarttutor.learning.storage.LearningStore`.
- Mastery math remains in `smarttutor.learning.mastery.compute_mastery`.
- Mastery thresholds remain in `smarttutor.learning.policy.gate_threshold`.
- Error classification remains in `smarttutor.learning.grading.classify_error`.
- No replacement RAG, OpenAI, Ollama, embedding, voice, document parsing, or attachment system was introduced.

## Tests Run

- `.venv\Scripts\python.exe -m pytest tests\api\test_notebook_router.py smarttutor\learning\tests\test_grading.py -q` — 36 passed.
- `python -m ruff check smarttutor\api\routers\sessions.py tests\api\test_notebook_router.py` — passed.
- `npx tsc --noEmit --pretty false` in `web` — passed.
- `npm run lint -- --quiet` in `web` — passed with existing warnings only; no errors.

## End-to-End Tests

- API-level quiz loop verified: quiz results submit successfully, notebook entries are written, learning progress is created, attempts are stored, a weak topic is created after a wrong answer, and the weak topic graduates after enough later correct evidence on the same topic.
- Real browser click-through, PDF upload, microphone recording, audio playback, and NVDA screen-reader testing were not rerun in this implementation pass.

## Remaining Issues

### P0

- Standalone Test/Exam/Call Exam product is still not implemented: no timer, marks, sections, final exam report, or saved exam history.
- Full browser RAG journey still needs fresh verification from upload through repeated cited questions.
- Full browser voice journey still needs fresh physical Record -> STT -> chat -> TTS playback verification.
- Progress remains split across several surfaces; quiz-derived mastery now exists, but a unified student dashboard still needs product work.

### P1

- Practice and Revision quick actions are still mostly prompt-driven entry points rather than fully deterministic adaptive loops from the UI.
- Multiple-select, matching, and numerical question controls are not verified as first-class quiz controls.
- Accessibility improved for quiz answer controls, but NVDA and keyboard-only passes across Tutor, Quiz, Practice, Revision, Progress, Voice, and Settings are still pending.

### P2

- Piper still needs voice model files before it can be considered available for local TTS.
- Suggestion quality and persona behavior still need real learner-history A/B checks.
- Settings still mix student-facing choices with admin/developer configuration.
