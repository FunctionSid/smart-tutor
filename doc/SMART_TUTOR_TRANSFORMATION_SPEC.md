# Smart Tutor Transformation Spec

Project: SmartTutor v1.5.16 to Smart Tutor  
Planned product name: Smart Tutor  
Planned attribution: Siddharth Kalantri, India  
Team: Siddharth and Sreedevi  
Status: Investigation and documentation only. No runtime behavior has been changed.

## 1. Purpose

This document describes how the current SmartTutor project can be transformed
into Smart Tutor using 4 practical phases instead of many small phases.

Smart Tutor should become an accessible AI tutor where users upload books,
PDFs, and learning documents, then ask the system to teach, explain,
simplify, summarize, quiz, test, revise, and track progress from those
materials.

## 2. Current SmartTutor Architecture

SmartTutor is a full agent-native learning platform. It contains a Python
backend, Typer CLI, FastAPI API, WebSocket streaming runtime, Next.js frontend,
RAG/document processing, memory, notebooks, question banks, learning paths,
partners, skills, MCP, providers, and optional visualization/math animation.

### Core Runtime

| Component | Current Purpose | Location | Core/Optional | Removal Risk |
|---|---|---|---|---|
| Unified context | Shared turn request object | `smarttutor/core/context.py` | Core | Removing breaks CLI/API/web turn execution |
| Orchestrator | Routes a turn to a capability and streams events | `smarttutor/runtime/orchestrator.py` | Core | High, central runtime |
| Stream events | Structured streaming event protocol | `smarttutor/core/stream.py`, `smarttutor/core/stream_bus.py` | Core | High, frontend and CLI depend on it |
| Capability registry | Loads registered capabilities | `smarttutor/runtime/registry/capability_registry.py` | Core | High |
| Tool registry | Loads registered tools | `smarttutor/runtime/registry/tool_registry.py` | Core | High |
| App facade | Python SDK-like wrapper used by CLI | `smarttutor/app/facade.py` | Core/useful | Medium-high |

The main built-in capabilities are confirmed in
`smarttutor/runtime/bootstrap/builtin_capabilities.py`:

- `chat`
- `deep_solve`
- `deep_question`
- `deep_research`
- `math_animator`
- `visualize`
- `mastery_path`
- `immersive_reading`

### Backend/API

Backend technology:

- Python 3.11 to <3.14
- FastAPI
- Uvicorn
- WebSockets
- Pydantic
- aiosqlite
- PocketBase integration where configured

Main files:

- `smarttutor/api/main.py`
- `smarttutor/api/routers/unified_ws.py`
- `smarttutor/runtime/launcher.py`
- `smarttutor_cli/main.py`

Confirmed API router areas include:

- auth
- outputs
- multi-user
- chat
- question
- knowledge
- imports
- dashboard
- learning/mastery path
- co-writer
- notebook
- book
- reading
- memory
- capabilities settings
- sessions
- question notebook
- settings
- MCP settings
- space MCP
- CLI apps
- skills
- subagents
- personas
- tools
- system
- voice
- plugins
- agent config
- partners
- attachments
- MarginNote 4
- unified WebSocket
- quiz judge

### WebSocket/Streaming

The main WebSocket endpoint is:

- `/api/v1/ws`

Confirmed message types in `smarttutor/api/routers/unified_ws.py` include:

- `message` / `start_turn`
- `ping`
- `subscribe_turn`
- `subscribe_session`
- `check_active_turn`
- `resume_from`
- `unsubscribe`
- `cancel_turn`
- `submit_user_reply`
- `regenerate`
- `user_input`

This should be kept for Smart Tutor because it powers streaming answers,
tool-call traces, loading states, cancellation, regeneration, and agent pauses.

### Frontend

Frontend technology:

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- i18next/react-i18next
- Framer Motion
- lucide-react
- Chart.js/react-chartjs-2
- Mermaid
- PDF.js
- docx-preview
- exceljs
- react-markdown with math/code support

Main frontend areas:

- `web/app/(workspace)/home/[[...sessionId]]/page.tsx`: main chat workspace
- `web/app/(workspace)/book/page.tsx`: current standalone Book product
- `web/app/(workspace)/co-writer/page.tsx`: co-writer product
- `web/app/(workspace)/partners/*`: partner UI
- `web/app/(utility)/knowledge/page.tsx`: Knowledge Center
- `web/app/(utility)/memory/*`: memory UI and graph
- `web/app/(utility)/space/*`: learning space, skills, questions, personas, notebooks
- `web/app/(utility)/settings/*`: settings surfaces
- `web/app/(auth)/*`: login/register
- `web/app/(admin)/*`: admin users

### CLI

CLI technology:

- Typer
- Rich
- prompt_toolkit

Main CLI file:

- `smarttutor_cli/main.py`

Confirmed commands include:

- `smarttutor run`
- `smarttutor start`
- `smarttutor serve`
- `smarttutor chat`
- `smarttutor kb`
- `smarttutor memory`
- `smarttutor partner`
- `smarttutor skill`
- `smarttutor plugin`
- `smarttutor config`
- `smarttutor session`
- `smarttutor notebook`
- `smarttutor provider`
- `smarttutor book`

For Smart Tutor, the CLI can be kept internally for development/admin use.

## 3. Current AI, RAG, And Provider Stack

### LLM Providers

Provider abstraction is confirmed in:

- `smarttutor/services/provider_registry.py`
- `smarttutor/services/llm`
- `smarttutor/services/config/provider_runtime.py`
- settings pages under `web/app/(utility)/settings`

Confirmed provider registry includes OpenAI, Anthropic, Azure OpenAI, OpenAI
Codex, GitHub Copilot, CodeBuddy, DeepSeek, Gemini, Zhipu, DashScope, Moonshot,
MiniMax, Mistral, StepFun, Xiaomi MIMO, vLLM, Ollama, LM Studio, llama.cpp,
Lemonade, OpenVINO Model Server, NVIDIA NIM, Groq, Qianfan, and multiple
gateways such as OpenRouter, OrcaRouter, Eden AI, AiHubMix, SiliconFlow,
Novita, Atlas Cloud, VolcEngine, and BytePlus.

Smart Tutor should initially keep:

- OpenAI cloud models
- Ollama local models
- local embedding support through Ollama-compatible embedding settings

Confirmed current behavior:

- OpenAI and Ollama are already represented in the current provider
  abstraction.
- Ollama/local model choices must be discovered from the local Ollama runtime
  where possible, not hard-coded into Smart Tutor workflows.
- The user's current Windows development machine has been reported to include
  local Ollama models such as `qwen3:8b`, `qwen3:4b`, `qwen25-coder`,
  `qwen25-coder-14b`, and `llama3`, but these are examples of one machine's
  state and must not be treated as permanent product defaults.

China-specific or extra gateways should be hidden first, then removed after
tests confirm they are unused.

### RAG/Knowledge

Confirmed locations:

- `smarttutor/knowledge`
- `smarttutor/services/rag`
- `smarttutor/services/rag/factory.py`
- `smarttutor/services/parsing`
- `smarttutor/tools/rag_tool.py`
- `smarttutor/api/routers/knowledge.py`
- `web/app/(utility)/knowledge/page.tsx`

Confirmed RAG providers in `smarttutor/services/rag/factory.py`:

- `llamaindex`: default local vector retrieval with hybrid BM25/vector fusion
- `pageindex`: PageIndex Cloud
- `pageindex-oss`: local PageIndex library
- `graphrag`: optional local knowledge graph retrieval
- `lightrag`: optional graph/vector retrieval
- `lightrag-server`: external LightRAG server
- `ima`: Tencent IMA external knowledge base

Confirmed retrieval/indexing dependencies:

- `llama-index`
- `llama-index-retrievers-bm25`
- `llama-index-vector-stores-faiss`
- `faiss-cpu`
- `pageindex`
- optional `graphrag`
- optional `raganything`/LightRAG

For Smart Tutor, RAG and document processing are core. Do not remove these in
early phases.

Embedding requirements:

- Keep SmartTutor's existing embedding/RAG architecture.
- Do not replace the RAG system merely to support Ollama.
- Treat embedding providers as interchangeable providers behind the existing
  architecture.
- Support OpenAI embeddings for cloud/Railway deployments.
- Support Ollama embeddings for the local Windows/development profile.
- Default local embedding target should be Ollama `nomic-embed-text` where it
  is installed or can be configured.
- Associate embedding provider/model metadata with the relevant knowledge
  base/index.
- If the embedding provider/model changes and the existing vector index is
  incompatible, Smart Tutor must require or recommend re-indexing instead of
  silently using incompatible vectors.

### Document Processing

Confirmed dependencies and modules show support for:

- PDF: PyMuPDF, pypdf, pdfplumber
- Office: python-docx, openpyxl, python-pptx
- parsing engines: MarkItDown, Docling, PyMuPDF4LLM, LiteParse, Tika, MinerU
  configuration/integration
- frontend previews: PDF.js, docx-preview, exceljs

Smart Tutor should keep document ingestion, parsing, accessible text extraction,
chapter/section structure, and source citation support.

### Voice, STT, And TTS Providers

Confirmed current behavior:

- SmartTutor already exposes voice routes through `smarttutor/api/routers/voice.py`.
- Existing routes include request-response STT and TTS:
  - `POST /api/v1/voice/stt`
  - `POST /api/v1/voice/tts`
- Existing voice runtime configuration is resolved through
  `smarttutor/services/config/provider_runtime.py`.
- Existing voice adapters live under `smarttutor/services/voice/adapters`.
- Current implemented adapters are OpenAI-compatible HTTP adapters, including
  special OpenRouter TTS handling.
- Existing frontend controls include microphone dictation and assistant-message
  read-aloud.

Planned Smart Tutor behavior:

- Preserve SmartTutor's existing STT endpoint architecture.
- Preserve SmartTutor's existing TTS endpoint architecture.
- Preserve provider resolution, settings, frontend controls, and existing error
  handling.
- Add local adapters instead of replacing the current voice system.
- Support OpenAI STT/TTS in both local and Railway profiles.
- Support local STT in the Windows/development profile, with `faster-whisper` as
  the primary candidate to investigate.
- Support local TTS in the Windows/development profile through:
  - Windows SAPI / installed Windows voices
  - Piper
  - Kokoro

Items requiring investigation before implementation:

- `faster-whisper`: Windows support, Linux compatibility, CPU/RAM needs,
  latency, language support, accessibility behavior, licensing, and streaming
  capability.
- Windows SAPI: installed voice discovery, service/runtime permissions, output
  format, Windows-only guards, and accessibility behavior.
- Piper: current project status, voice/model packaging, Windows/Linux support,
  latency, licensing, and deployment fit.
- Kokoro: current implementation maturity, model/voice licensing, Windows/Linux
  support, CPU/GPU needs, quality, latency, and OpenAI-compatible wrapper
  options.

Items requiring implementation:

- Local STT adapter registration.
- Local TTS adapter registration.
- Provider visibility rules by deployment profile.
- Settings UI simplification for normal users.
- Accessibility-first voice status announcements and keyboard-only operation.

## 4. Current Feature Areas

| Feature | What It Does | Location | Smart Tutor Direction |
|---|---|---|---|
| Chat | Agentic chat with tools and streaming | `smarttutor/agents/chat`, `web/app/(workspace)/home` | KEEP/MODIFY |
| Deep Solve | Multi-stage problem solving | `smarttutor/capabilities/solve` | KEEP if useful for tutoring |
| Deep Research | Research pipeline using search/tools | `smarttutor/agents/research` | MODIFY/optional |
| Deep Question | Question generation | `smarttutor/agents/question` | KEEP/MODIFY for quizzes |
| Visualize | SVG/HTML/Chart/Mermaid visual explanations | `smarttutor/agents/visualize` | KEEP optional, simplify |
| Math Animator | Manim-based animation | `smarttutor/agents/math_animator` | HIDE/optional |
| Mastery Path | Guided learning and grading | `smarttutor/capabilities/mastery`, `smarttutor/learning` | KEEP/MODIFY |
| Immersive Reading | Reading materials with reading tools | `smarttutor/capabilities/reading`, `smarttutor/reading` | KEEP/MODIFY heavily |
| Knowledge Center | Knowledge base creation/retrieval | `smarttutor/knowledge`, `web/app/(utility)/knowledge` | KEEP/MODIFY into My Library |
| Memory | L1/L2/L3 memory and personalization | `smarttutor/services/memory`, `web/app/(utility)/memory` | KEEP but make user-controlled |
| Notebook | Saved notes/records | `smarttutor/services/notebook`, `web/app/(utility)/notebook` | KEEP optional |
| Book product | Generates standalone living books | `smarttutor/book`, `web/app/(workspace)/book` | REPLACE UI with Smart Tutor Library/Book learning |
| Co-Writer | Writing assistant | `smarttutor/co_writer`, `web/app/(workspace)/co-writer` | REMOVE/HIDE |
| Partners | IM-connected companions | `smarttutor/partners`, `smarttutor/services/partners` | REMOVE/HIDE |
| MCP | External tool/server integration | `smarttutor/services/mcp` | KEEP internally, hide initially |
| Skills/plugins | Extensibility layer | `smarttutor/skills`, `smarttutor/plugins` | KEEP internally, hide from normal users |
| Voice/STT/TTS | Voice routes/settings | `smarttutor/api/routers/voice.py`, settings STT/TTS pages | KEEP/MODIFY for accessibility |
| Auth/admin | Login/register/admin users | `smarttutor/api/routers/auth.py`, `web/app/(auth)`, `web/app/(admin)` | INVESTIGATE based on deployment |

## 5. Accessibility: Current State Vs Smart Tutor Requirement

Current state confirmed by source inspection:

- Many components use `aria-label`, `aria-hidden`, `aria-expanded`, `role`,
  `aria-live`, and focus styles.
- `web/components/common/Modal.tsx` includes dialog role, `aria-modal`, initial
  focus, focus restoration, and focus trap behavior.
- `web/components/common/AssistantResponse.tsx` uses `role="article"` and
  `aria-live="polite"` for assistant replies.
- Reading resize handles expose keyboard behavior and separator roles.
- Some settings toggles use `role="switch"` and `aria-checked`.

Not confirmed from repository inspection:

- Full NVDA compatibility.
- Complete screen-reader-first workflow.
- WCAG conformance level.
- Accessible math rendering quality across all output types.
- Complete keyboard-only coverage for every page.
- Whether all streaming states are announced consistently.

Smart Tutor requirements:

- NVDA compatibility testing.
- Semantic HTML landmarks.
- Correct heading hierarchy.
- Keyboard-only navigation.
- Visible focus state.
- No keyboard traps.
- Accessible chat history.
- Accessible streaming announcements.
- Accessible loading and error states.
- Accessible dialogs, menus, tabs, switches, forms, and file uploads.
- Accessible quiz/test interface.
- Accessible mathematical content.
- Text alternative for PDF canvas or visually inaccessible document previews.
- TTS/read-aloud.
- Voice input.
- Screen-reader-first My Library and reading experience.

Voice accessibility requirements:

- Microphone controls must be keyboard accessible.
- Recording state must be announced.
- Transcription state must be announced.
- Transcription completion must be announced.
- Voice/STT/TTS errors must be announced.
- TTS playback controls must be keyboard accessible.
- Play, pause, and stop controls must have accessible names.
- Focus must not be lost during recording or playback.
- Audio must never be the only way information is provided.
- Transcripts must remain accessible.
- Loading states must be announced.
- Voice controls must work without requiring a mouse.
- NVDA testing must include microphone dictation, transcription results,
  read-aloud controls, autoplay settings, loading states, and error states.

Current gaps requiring investigation before implementation:

- Whether microphone recording and transcription state changes are announced
  through a reliable live region.
- Whether read-aloud loading/playback/stop states are announced consistently.
- Whether focus remains stable while microphone permission prompts, recording,
  transcription, TTS generation, and playback happen.
- Whether settings pages expose only understandable options to screen-reader
  users instead of the full developer/provider catalog complexity.

## 6. LangChain And LangGraph Investigation

Confirmed from repository inspection:

- No direct `langchain` dependency was found in `pyproject.toml`.
- No direct `langgraph` dependency was found in `pyproject.toml`.
- Source search did not reveal direct LangChain/LangGraph usage as a main
  framework.
- Existing orchestration is handled by SmartTutor's own `ChatOrchestrator`,
  capability registry, tool registry, StreamBus, and agent pipelines.
- Existing RAG is handled mainly by SmartTutor services on top of LlamaIndex,
  PageIndex, GraphRAG, LightRAG, LightRAG Server, and IMA.
- Existing tools use SmartTutor's `BaseTool` and `ToolDefinition` protocol.

Recommendation:

Do not replace SmartTutor's working runtime with LangChain or LangGraph in the
early transformation. It would duplicate capabilities, tools, memory routing,
streaming, and RAG contracts that already exist.

Potential use of LangGraph:

- Add it later as an optional Smart Tutor workflow layer for one high-value
  workflow, such as:
  - document diagnosis
  - teaching plan
  - quiz/practice loop
  - weak-topic revision loop

Proposed integration shape:

```text
Smart Tutor UI
  |
  v
Existing WebSocket/API turn runtime
  |
  v
Smart Tutor capability
  |
  v
Optional LangGraph workflow for tutor planning/practice
  |
  v
Existing SmartTutor services:
RAG, tools, memory, sessions, provider abstraction
  |
  v
OpenAI or Ollama
```

LangGraph should sit inside a new Smart Tutor capability, not above the entire
SmartTutor orchestrator. That keeps existing WebSocket streaming, settings,
sessions, RAG, tools, and UI contracts intact.

Potential LangChain use:

- Utility integrations where it clearly helps.
- Wrapping selected retrievers/tools if needed.
- Not recommended as a replacement for current RAG or tool registry at first.

Risks:

- Duplicates existing orchestration.
- Adds new dependency and mental model.
- Can complicate streaming event mapping.
- Can create performance overhead in multi-node workflows.
- May make debugging harder if both SmartTutor and LangGraph own control flow.

Decision for now:

- Phase 1: document only.
- Phase 2/3: do not add LangChain/LangGraph yet.
- Phase 4: consider a small prototype only if existing capability pipelines
  cannot express the desired Smart Tutor practice workflow cleanly.

## 7. Four-Phase Migration Plan

### Phase 1: Understand And Document

Goal:

Create accurate documentation and a transformation plan.

What changes:

- Create this spec.
- Inventory current architecture.
- Identify keep/modify/remove/replace candidates.
- Identify "do not touch yet" areas.
- Decide initial Smart Tutor scope.
- Document current SmartTutor voice/STT/TTS architecture.
- Document current voice provider adapters.
- Document current embedding/RAG architecture.
- Document current OpenAI support.
- Document current Ollama support and model discovery requirement.
- Document the two deployment profiles: local Windows/development and Railway
  production.
- Investigate local voice candidates without installing them:
  - `faster-whisper`
  - Windows SAPI / installed Windows voices
  - Piper
  - Kokoro
- Capture Railway constraints:
  - OpenAI-only production AI defaults
  - Linux compatibility
  - no local model files
  - no Windows-specific runtime dependency
  - credentials from environment variables/secrets

What must not change:

- Runtime behavior.
- Production code.
- Dependencies.
- Branding assets.
- Feature availability.

Dependencies:

- Repository inspection.
- README, package metadata, backend routes, frontend routes, registries, RAG
  factory, provider registry, settings, tests.

Tests required:

- No runtime tests required because only documentation changes.
- `git status` should show only docs added/changed.

Rollback:

- Remove or edit the Markdown spec.

### Phase 2: Rebrand And Simplify UI

Goal:

Make the application visibly become Smart Tutor while hiding confusing product
areas from normal users.

What changes:

- Replace user-facing SmartTutor branding with Smart Tutor.
- Update browser title, metadata, visible nav branding, logos/icons/favicon,
  empty states, and user-facing text.
- Add attribution: Siddharth Kalantri, India.
- Simplify main navigation.
- Hide Co-Writer, Partners, standalone Book product, plugin marketplace, CLI
  apps, advanced MCP/settings pages, image/video generation, and extra provider
  choices from normal user flows.
- Simplify Settings so normal users can independently choose:
  - AI/chat provider and model
  - embedding provider and model
  - STT provider and model
  - TTS provider and model/voice
- Show only providers available for the active deployment profile.
- For the local profile, expose:
  - Chat: OpenAI or Ollama
  - Embeddings: OpenAI or Ollama
  - STT: OpenAI or local
  - TTS: OpenAI, Windows SAPI, Piper, or Kokoro
- For the Railway profile, expose:
  - Chat: OpenAI
  - Embeddings: OpenAI
  - STT: OpenAI
  - TTS: OpenAI
- Hide Ollama/local-only choices in Railway profile because they are
  unavailable there.
- Make Settings accessibility-first:
  - keyboard-operable provider/model selection
  - accessible names and descriptions
  - announced loading/error states
  - no exposure of unnecessary SmartTutor developer complexity

What must not change:

- Python import package name at first.
- `ChatOrchestrator`.
- Stream event schema.
- WebSocket protocol.
- Core RAG/document processing.
- Existing APIs until UI no longer calls them.
- Backend code for hidden features; hide first, delete later only after tests.
- Existing provider abstraction.

Dependencies:

- `web/public`
- `web/locales`
- app layout/navigation components
- settings pages
- frontend route guards/navigation

Tests required:

- Frontend build.
- Frontend node tests where practical.
- Manual smoke test: open app, start chat, open settings, upload file if enabled.

Rollback:

- Revert branding/nav changes.
- Since backend is not removed, hidden features can be restored by re-enabling
  navigation.

### Phase 3: Build Smart Tutor Core Experience

Goal:

Build the real Smart Tutor learning workflow around documents, accessible
reading, tutoring, quizzes, revision, progress, OpenAI, and Ollama.

What changes:

- Turn Knowledge Center into or alongside "My Library".
- Support books, PDFs, and documents as first-class learning materials.
- Keep book ingestion and document structure, but replace the separate Book
  product feeling with a unified Library/Reader/Tutor experience.
- Add Smart Tutor actions:
  - Ask questions
  - Teach me
  - Explain
  - Simplify
  - Summarize
  - Quiz
  - Test
  - Practice
  - Revise
  - Identify weak topics
  - Track learning progress
- Adapt `mastery_path`, `deep_question`, `immersive_reading`, RAG, memory, and
  sessions into the main product flow.
- Configure OpenAI cloud model path.
- Configure Ollama local model path.
- Discover installed Ollama models dynamically for local chat selection where
  technically supported, instead of hard-coding model names.
- Configure local embeddings, especially Ollama with `nomic-embed-text`, if
  supported by existing embedding settings or with a small adapter if needed.
- Preserve existing RAG/indexing architecture while making OpenAI/Ollama
  embedding providers selectable.
- Track embedding provider/model metadata with knowledge bases and require or
  recommend re-indexing when indexes are incompatible with a changed embedding
  model.
- Implement local STT after investigation, with `faster-whisper` as the primary
  candidate unless investigation identifies a better fit.
- Implement local TTS options for the local Windows/development profile:
  - Windows SAPI / installed Windows voices, including voice discovery where
    technically possible
  - Piper as the lightweight local TTS option
  - Kokoro as the higher-quality local TTS option
- Preserve the existing voice endpoint/provider/adapter architecture while
  adding local adapters.
- Add accessible voice interaction:
  - keyboard-accessible microphone controls
  - announced recording/transcription/playback/loading/error states
  - stable focus during recording and playback
  - accessible transcripts
  - mouse-free voice workflows
- Improve accessibility of chat, reading, file upload, quiz, math, and streaming
  output.

What must not change:

- Existing RAG pipeline contract.
- Existing provider abstraction unless an extension is needed.
- Session/turn storage contract.
- WebSocket event protocol.
- Core tool/capability registration rules.

Dependencies:

- `smarttutor/knowledge`
- `smarttutor/services/rag`
- `smarttutor/services/parsing`
- `smarttutor/capabilities/reading`
- `smarttutor/reading`
- `smarttutor/learning`
- `smarttutor/capabilities/mastery`
- `smarttutor/agents/question`
- `smarttutor/services/memory`
- `web/components/reading`
- `web/components/chat`
- `web/app/(utility)/knowledge`
- `web/app/(workspace)/home`

Tests required:

- Upload and index PDF.
- Ask question from uploaded document.
- Citation/source test.
- Quiz generation test.
- Practice/grading test.
- Session resume/regenerate test.
- OpenAI provider smoke test.
- Ollama provider smoke test.
- Embedding/index version test.
- Local STT smoke test.
- Local TTS smoke test.
- Windows SAPI voice discovery/playback test on Windows.
- Piper local TTS smoke test where installed.
- Kokoro local TTS smoke test where installed.
- Keyboard-only navigation pass.
- Screen-reader/NVDA manual pass.

Rollback:

- Keep old Knowledge Center and existing capabilities until Smart Tutor flows
  are stable.
- Feature-flag new Library/Tutor flows where possible.

### Phase 4: Cleanup, Remove, And Production Harden

Goal:

After Smart Tutor works, remove unused systems safely and prepare for production.

What changes:

- Remove or fully disable Co-Writer if no longer needed.
- Remove or fully disable Partners/IM channels if no longer needed.
- Remove separate standalone Book UI after Smart Tutor Library replaces it.
- Remove unnecessary China-specific provider/search integrations if they are no
  longer exposed or referenced.
- Remove unnecessary video/image-generation product functionality if not part of
  Smart Tutor.
- Remove unused frontend pages, routes, dependencies, and tests.
- Remove unused backend routers, services, dependencies, and config pages.
- Harden Docker/deployment/startup configuration.
- Decide whether auth/admin stays.
- Add accessibility regression checks.
- Validate the local Windows/development profile:
  - OpenAI chat path
  - Ollama chat path
  - OpenAI embeddings
  - Ollama embeddings
  - local `nomic-embed-text` indexing where configured
  - OpenAI STT/TTS
  - local STT/TTS
  - Windows SAPI voice discovery where available
- Validate the Railway production profile:
  - OpenAI chat only
  - OpenAI embeddings only
  - OpenAI STT only
  - OpenAI TTS only
  - no requirement for Ollama, Qwen models, Nomic models, `nomic-embed-text`,
    `faster-whisper`, Piper, Kokoro, Windows SAPI, Windows-only dependencies, or
    local model files
- Validate Linux portability.
- Validate Railway `$PORT`, health checks, WebSockets, storage, upload limits,
  environment variables/secrets, and OpenAI-only production configuration.
- Clean unused dependencies only after local and Railway profiles pass.
- Prepare GitHub readiness and Railway deployment readiness.
- Consider optional LangGraph prototype only if Phase 3 shows real need.

What must not change:

- Working Smart Tutor Library/RAG/tutor flow.
- WebSocket streaming contract unless frontend and backend are migrated together.
- User data layout without a migration plan.

Dependencies:

- Test coverage and manual verification from Phase 3.
- Import graph checks.
- Package dependency checks.
- Docker/build checks.

Tests required:

- Full backend test suite where practical.
- Frontend build.
- Frontend node tests.
- API startup test.
- WebSocket chat smoke test.
- Document upload/RAG smoke test.
- Accessibility audit and NVDA manual verification.
- Voice accessibility audit and NVDA manual verification.
- Docker Compose startup test if production uses Docker.
- Railway production build/readiness test.

Rollback:

- Remove features in small commits.
- Keep a branch/tag before deletion.
- Prefer hiding before deleting.
- Restore removed router/page/dependency from version control if breakage appears.

## 8. Keep / Modify / Remove / Replace Table

| Component | Current Purpose | Location | Decision | Planned Smart Tutor Role | Risk |
|---|---|---|---|---|---|
| Core backend | Runtime services and app logic | `smarttutor` | KEEP | Foundation | High if changed carelessly |
| FastAPI API | HTTP/WebSocket backend | `smarttutor/api` | KEEP | Backend API | High |
| WebSocket streaming | Live turn events | `smarttutor/api/routers/unified_ws.py` | KEEP | Streaming tutor responses | High |
| Orchestrator | Capability routing | `smarttutor/runtime/orchestrator.py` | KEEP | Main turn router | High |
| Capability registry | Capability loading | `smarttutor/runtime/registry` | KEEP | Add Smart Tutor capability | High |
| Tool registry | Tool loading | `smarttutor/runtime/registry` | KEEP | Tutor tools | High |
| Chat capability | Agentic chat | `smarttutor/agents/chat` | MODIFY | Smart Tutor chat | Medium |
| RAG | Document retrieval | `smarttutor/services/rag` | KEEP/MODIFY | Core document tutor | High |
| Knowledge Center | KB management | `smarttutor/knowledge`, UI knowledge page | REPLACE/MODIFY | My Library | Medium-high |
| Document parsing | Extract content | `smarttutor/services/parsing` | KEEP | PDF/book/doc support | High |
| PageIndex | Document/RAG engine | `smarttutor/services/rag/pipelines/pageindex` | KEEP optional | Advanced document reading | Medium |
| LlamaIndex/FAISS/BM25 | Local retrieval | `smarttutor/services/rag/pipelines/llamaindex` | KEEP | Default local RAG | High |
| Memory | Personalization | `smarttutor/services/memory` | KEEP/MODIFY | Learning memory | Medium-high |
| Sessions | Chat history/turn runtime | `smarttutor/services/session` | KEEP | Learning continuity | High |
| Mastery/learning | Guided learning | `smarttutor/learning`, `smarttutor/capabilities/mastery` | MODIFY | Progress and weak topics | Medium |
| Question generation | Creates questions | `smarttutor/agents/question` | MODIFY | Quiz/test/practice | Medium |
| Immersive reading | Document reading | `smarttutor/capabilities/reading`, `smarttutor/reading` | MODIFY | Accessible reader | Medium-high |
| Current Book UI | Standalone book product | `web/app/(workspace)/book` | REPLACE | Unified Library/Book learning | Medium |
| Book backend | Book compilation | `smarttutor/book` | INVESTIGATE/KEEP parts | Chapters/sections/content structure | Medium |
| Co-Writer | Writing assistant | `smarttutor/co_writer`, co-writer UI/API | REMOVE later | Not core | Medium |
| Partners | IM companions | `smarttutor/partners`, `smarttutor/services/partners` | REMOVE later | Not core | Medium-high |
| MCP | External tools | `smarttutor/services/mcp` | KEEP internally | Future integrations | Medium |
| Skills/plugins | Extensibility | `smarttutor/skills`, `smarttutor/plugins` | KEEP/HIDE | Internal extensibility | Medium |
| Voice/STT/TTS | Audio input/output | `smarttutor/api/routers/voice.py`, settings pages | KEEP/MODIFY | Accessibility/audio tutoring | Medium |
| Image/video generation | Media generation tools/settings | `smarttutor/tools/media_gen_tool.py`, settings image/video | REMOVE/HIDE | Not initial core | Low-medium |
| OpenAI provider | Cloud LLM | provider registry/settings | KEEP | Primary cloud model | Low |
| Ollama provider | Local LLM | provider registry/settings | KEEP/MODIFY | Local model path | Medium |
| China-specific providers | Extra provider support | provider registry/settings/icons | HIDE then REMOVE | Not initial core | Medium |
| Search providers | Web search | `smarttutor/tools/web_search.py`, settings search | MODIFY | Optional web support | Medium |
| Auth/admin | Users/admin | auth/admin routes/UI | INVESTIGATE | Needed for hosted product | Medium-high |
| CLI | Developer/admin entry | `smarttutor_cli` | KEEP internally | Dev tooling | Low-medium |
| Frontend app shell | Navigation/layout | `web/components/layout`, `web/app` | MODIFY | Smart Tutor UI | Medium |
| Tests | Regression coverage | `tests`, `web/tests` | KEEP/MODIFY | Safety net | High if ignored |

## 9. Do Not Touch Yet

Do not delete or heavily rewrite these during early phases:

- `smarttutor/runtime/orchestrator.py`
- `smarttutor/core/context.py`
- `smarttutor/core/stream.py`
- `smarttutor/core/stream_bus.py`
- `smarttutor/runtime/registry/*`
- `smarttutor/api/routers/unified_ws.py`
- `smarttutor/services/session`
- `smarttutor/services/config`
- `smarttutor/services/llm`
- `smarttutor/services/rag`
- `smarttutor/services/parsing`
- `web/lib/unified-ws.ts`
- main chat page and chat components
- `pyproject.toml` dependency removals

These are central to runtime behavior. Modify them only with tests and a clear
migration reason.

## 10. Important Findings

- The 4-phase plan is technically sound if deletion is delayed until Phase 4.
- Smart Tutor should reuse SmartTutor's existing runtime instead of starting from
  scratch.
- RAG/document processing is already strong and should become the heart of My
  Library.
- The separate Book product should not simply be deleted at first. Its useful
  ingestion/structure concepts may support Smart Tutor's book/document learning.
- Partners and Co-Writer are not core to the Smart Tutor vision and are good
  candidates to hide early and remove later.
- LangChain/LangGraph are not currently core dependencies. LangGraph may be
  useful later inside one Smart Tutor capability, but replacing the existing
  orchestrator would be risky and duplicative.
- Accessibility has visible foundations in the code, but full NVDA/accessibility
  compliance is not confirmed from repository inspection.

## 11. Verification Performed

Repository areas inspected:

- Root project structure.
- `README.md`.
- `pyproject.toml`.
- `web/package.json`.
- Backend API startup and router registration.
- Unified WebSocket router.
- Runtime orchestrator.
- Capability registry list.
- Tool registration source.
- Provider registry.
- RAG factory.
- Frontend route tree.
- CLI entry point.
- App facade.
- Accessibility-related frontend markers.
- LangChain/LangGraph references through source/dependency search.

Confirmed:

- SmartTutor has its own orchestration and tool/capability system.
- SmartTutor directly uses LlamaIndex/PageIndex-style RAG infrastructure.
- OpenAI and Ollama are represented in the provider registry.
- WebSocket streaming is central to the app.
- Many advanced systems are separate enough to hide first.

Uncertain/not confirmed:

- Full accessibility compliance.
- Whether `nomic-embed-text` is already a named preset in embedding settings.
  Ollama local provider support is confirmed, but this exact embedding model
  should be verified in settings/runtime before implementation.
- Which frontend navigation component should be edited first for final Smart
  Tutor IA; this requires a focused UI pass.
- Whether production deployment will be single-user local, hosted multi-user, or
  hybrid.

## 12. Final Recommendation

Use 4 phases:

1. Understand and document.
2. Rebrand and simplify UI.
3. Build Smart Tutor core learning experience.
4. Cleanup, remove unused systems, and production harden.

This keeps the work understandable while still protecting the existing program.
The safest principle is: keep the engine, reshape the product, hide before
delete, and remove only after tests prove the new Smart Tutor flow works.

## 13. GitHub Repository Plan

Smart Tutor's GitHub repository has been created.

Repository:

- Owner: `FunctionSid`
- Repository: `FunctionSid/smart-tutor`
- URL: `https://github.com/FunctionSid/smart-tutor`
- Intended primary branch: `main`

Current state:

- The GitHub repository exists.
- The repository is currently empty.
- Nothing from the local SmartTutor project has been pushed yet.
- Development must continue locally first.
- The repository should receive the finished/tested Smart Tutor project later,
  after documentation, rebranding, simplification, tests, and secret checks.

Local development path:

- `D:\project\smart-tutor`

Important portability rule:

- This Windows path is only the current developer machine path.
- It must never be treated as a production path.
- Production code must not hard-code `D:\project\smart-tutor`,
  `C:\Users\Sourabh`, or any other developer-specific absolute path.

## 14. GitHub Readiness Requirements

Smart Tutor must eventually be safe to push to GitHub.

Hard requirements:

- No secrets committed to GitHub.
- OpenAI API keys must never be hard-coded.
- `.env` must not be committed.
- `.env` must remain listed in `.gitignore`.
- Provide a Smart Tutor `.env.example` with variable names only and no secrets.
- No absolute Windows paths in production code.
- No hard-coded `D:\project\smart-tutor` paths.
- No hard-coded `C:\Users` paths.
- Use `pathlib`, runtime home, configurable data directories, or environment
  variables for filesystem paths.
- Application must work on Windows during development.
- Application must work on Linux in production.
- Avoid Windows-specific runtime assumptions unless guarded by platform checks.
- Configuration must come from environment/settings, not machine-specific paths.
- Document required environment variables.
- Keep development, testing, and production configuration separate.
- GitHub should contain source code, docs, and configuration templates only.
- Do not commit private credentials.
- Do not commit Ollama model files.
- Do not commit large local vector databases or indexes unless deliberately
  versioned for a specific reason.
- Document generated/local directories that must remain ignored.

Current `.gitignore` findings:

- `.env`, `*.env`, `*.env.local`, and virtual environments are ignored.
- `data/` is ignored, which protects runtime settings, user data, knowledge
  bases, memory, indexes, sessions, and local outputs from accidental commits.
- `run_code_workspace/` is ignored.
- generated output/cache/log/database/media files are broadly ignored.
- `.vscode/` is ignored except selected shared editor config files.
- `/docs/` is ignored, which is why current transformation docs are stored in
  `doc/` instead.
- `*.pdf` is ignored globally except demo PDFs. This protects local books/PDFs
  from commits, but future Smart Tutor sample documents must be deliberately
  allowlisted if needed.
- `*.db`, `*.sqlite`, and `*.sqlite3` are ignored, protecting local SQLite
  session and learning databases.

Potential GitHub issues to resolve before first push:

- Update `.env.example` for Smart Tutor. Current `.env.example` is mostly
  host-side compose configuration and does not document all future Smart Tutor
  provider variables.
- Confirm no local generated files under non-ignored folders need cleanup.
- Decide whether old SmartTutor docs/assets should remain, be replaced, or be
  rebranded before the first public Smart Tutor push.
- Keep `doc/SMART_TUTOR_TRANSFORMATION_SPEC.md` tracked; do not move it to
  ignored `/docs/`.
- Run a secret scan before the first push.

## 15. No Absolute Path Requirement

Smart Tutor must be portable.

Current confirmed path architecture:

- `smarttutor/runtime/home.py` resolves runtime home from:
  - explicit `home` argument
  - `SMARTTUTOR_HOME`
  - current working directory
- Runtime data lives below `<runtime-home>/data`.
- `smarttutor/services/path_service.py` centralizes the runtime storage layout.
- Many services use `pathlib.Path`.
- Docker uses `/app` as the container-internal application path. This is an
  expected container path, not a developer machine path.

Current absolute/developer path findings:

- No hard-coded `D:\project\smart-tutor` source-code dependency was found during
  inspection.
- No hard-coded `C:\Users\Sourabh` source-code dependency was found during
  inspection.
- Linux/container absolute paths such as `/app`, `/tmp`, `/proc`, and
  `/sys/fs/cgroup` exist where expected for Docker, health checks, or memory
  probes.
- Windows-specific behavior exists in guarded places, such as event loop policy
  handling for subprocess support on Windows and console encoding handling.
  These are compatibility accommodations, not production path dependencies.

Future requirements:

- Continue using `SMARTTUTOR_HOME`, `PathService`, `get_runtime_data_root()`,
  `pathlib`, and configuration values.
- Do not add absolute Windows paths to code, docs intended for deployment,
  tests, or configuration templates.
- Any cloud path must be configurable, container-relative, or provided by a
  mounted volume/object storage service.

## 16. Local Vs Cloud Architecture

Smart Tutor must use one codebase with two deployment/configuration profiles.
These profiles are not separate applications, forks, or divergent
implementations. The active profile determines which providers are available,
which defaults are selected, and which options appear in Settings.

Target local development architecture:

```text
Smart Tutor
  |
  |-- Chat Provider
  |   |-- OpenAI
  |   `-- Ollama
  |
  |-- Embedding Provider
  |   |-- OpenAI
  |   `-- Ollama
  |       `-- default local target: nomic-embed-text
  |
  |-- STT Provider
  |   |-- OpenAI
  |   `-- Local STT, primary candidate: faster-whisper
  |
  `-- TTS Provider
      |-- OpenAI
      |-- Windows SAPI / installed Windows voices
      |-- Piper
      `-- Kokoro
```

Current local Ollama models mentioned for development:

- `qwen3:8b`
- `qwen3:4b`
- `qwen25-coder`
- `qwen25-coder-14b`
- `llama3`

Rules:

- These model names are examples from the user's current Windows PC.
- Smart Tutor must discover installed Ollama models dynamically where possible
  rather than hard-coding these names.
- These model files must not be committed to GitHub.
- Railway must not be assumed to have access to the developer's local Ollama
  service.
- Cloud deployment must not depend on local Ollama.
- Ollama remains a local development/runtime option.
- Local Smart Tutor may support both cloud and local choices in the same UI.
- Windows SAPI is a required local TTS option because the Windows installation
  may contain additional installed voices.
- Piper and Kokoro must not be assumed installed; they are local options that
  require investigation and explicit setup.

Target cloud architecture:

```text
GitHub
  |
  v
Railway
  |
  v
Smart Tutor
  |
  |-- Chat Provider: OpenAI
  |-- Embedding Provider: OpenAI
  |-- STT Provider: OpenAI
  `-- TTS Provider: OpenAI
```

Provider abstraction requirement:

- The tutor code should use the existing provider abstraction rather than
  hard-coding OpenAI or Ollama directly in learning workflows.
- OpenAI should be the production/cloud provider.
- Ollama should be supported locally through provider configuration.
- Switching between OpenAI and Ollama must not require rewriting the tutor
  capability or UI flow.
- The same provider abstraction should cover chat, embeddings, STT, and TTS.
- Additional providers must be added as modular adapters/configuration entries,
  not as separate local/Railway implementations.

Settings visibility requirement:

- Local profile Settings should expose only:
  - Chat: OpenAI or Ollama
  - Embeddings: OpenAI or Ollama
  - STT: OpenAI or local
  - TTS: OpenAI, Windows SAPI, Piper, or Kokoro
- Railway profile Settings should expose only:
  - Chat: OpenAI
  - Embeddings: OpenAI
  - STT: OpenAI
  - TTS: OpenAI
- Ollama/local-only options should not appear as selectable Railway providers.
- Normal users should not see the full SmartTutor developer provider matrix
  unless an admin/advanced mode deliberately exposes it.

## 17. OpenAI Configuration Requirement

OpenAI remains the supported production/cloud provider.

The OpenAI API key must:

- never be committed
- never be hard-coded
- never appear in source control
- be supplied through environment/configuration
- work locally through `.env` or runtime settings
- work on Railway through Railway environment variables

Expected future configuration names to document in `.env.example`:

- `OPENAI_API_KEY`
- optional OpenAI-compatible base URL if Smart Tutor keeps a custom endpoint
  path
- model selection variables/settings if Smart Tutor chooses defaults outside
  the existing settings UI

Do not place any real secret in this spec or any committed config template.
When creating a future `.env` file, use a local-only entry like:

```env
OPENAI_API_KEY=replace_with_your_openai_api_key
```

For Railway, set `OPENAI_API_KEY` as a Railway environment variable/secret.
Never commit the real key to GitHub.

## 18. Railway Deployment Requirements

Smart Tutor must eventually be deployable to Railway.

Target production shape:

```text
GitHub
  |
  v
Railway
  |
  v
Smart Tutor application
  |
  |-- OpenAI
  `-- persistent application storage where required
```

Railway deployment rules:

- Railway deployment must not require Ollama.
- Railway deployment should use OpenAI for LLM and embedding where practical.
- Railway deployment should use OpenAI for STT and TTS.
- Local Ollama remains a local-only path.
- Railway must not require Qwen models, Nomic models, `nomic-embed-text`,
  `faster-whisper`, Piper, Kokoro, Windows SAPI, Windows-specific dependencies,
  or local model files.
- Railway must be Linux-compatible.
- OpenAI credentials must come from Railway environment variables/secrets.
- API keys must never be committed to GitHub.
- Do not assume unlimited free compute, RAM, or storage.
- Do not assume large model files can be hosted on Railway.
- Do not assume unlimited persistent storage.
- Railway free/low-cost resources should be treated as suitable for development,
  testing, and lightweight deployments.
- The production design should allow moving to larger Railway resources later
  without redesigning Smart Tutor.

Current Docker/deployment findings:

- The existing `Dockerfile` builds both Next.js frontend and FastAPI backend
  into one production image.
- It uses `supervisord` to run backend and frontend processes in the same
  container.
- Backend defaults to `BACKEND_PORT=8001`.
- Frontend defaults to `FRONTEND_PORT=3782`.
- The frontend script exports `PORT=${FRONTEND_PORT}` for Next.js.
- Health check calls the backend root URL and reads backend port from
  `/app/data/user/settings/system.json` when available.
- Docker compose mounts `./data:/app/data`.
- Compose also defines optional PocketBase and sandbox-runner sidecars.
- The current Docker setup is Docker/Compose-friendly but is not yet documented
  as Railway-ready.

Railway compatibility work likely required:

- Decide whether Railway should run one combined container or separate backend
  and frontend services.
- Make sure Railway's `PORT` environment variable is honored. Railway commonly
  expects the web process to listen on `$PORT`; the current all-in-one image has
  separate backend/frontend ports.
- Decide which service Railway exposes publicly: frontend, backend, or a
  single reverse-proxy entrypoint.
- Ensure WebSocket proxying works through Railway.
- Add a clear production start command for Railway.
- Add or adapt a health check endpoint/path suitable for Railway.
- Configure CORS and frontend/backend URLs for the Railway domain.
- Configure persistent storage for `data/` or replace local disk persistence
  with managed services/object storage.
- Confirm file permissions on Railway's Linux filesystem.
- Confirm graceful shutdown for backend, frontend, cron, event bus, partner
  manager if still present, MCP manager, and LLM clients.
- Confirm Next.js production standalone build works in Railway.
- Confirm logs go to stdout/stderr and do not rely only on files.

Architectural concern:

- A single Railway service exposing only one `$PORT` may not naturally fit the
  current two-port backend/frontend setup. A Railway deployment may need either:
  - one service running the Next.js frontend on `$PORT` with API/WebSocket proxy
    to a separate backend service
  - two Railway services, one backend and one frontend
  - a custom single-entry reverse proxy/supervisor design

Recommended production deployment architecture:

```text
GitHub repository
  |
  v
Railway project
  |
  |-- smart-tutor-web
  |   `-- Next.js frontend, public, listens on Railway $PORT
  |
  |-- smart-tutor-api
  |   `-- FastAPI backend, private/public as needed, WebSocket enabled
  |
  |-- persistent storage
  |   |-- Railway volume for small/dev deployments
  |   `-- external object/database/vector storage for production scale
  |
  `-- OpenAI via Railway environment variables
```

Alternative for earliest testing:

- Use one all-in-one Docker service if Railway routing and `$PORT` handling are
  adapted carefully. This is simpler to start but less clean for scaling.

## 19. Persistent Data Classification

Current SmartTutor persistence areas are centered around `data/`.

Confirmed storage locations/patterns:

- `data/user/settings`: runtime settings and provider configuration.
- `data/user/chat_history.db`: local SQLite session history.
- `data/user/workspace`: chat outputs, memory, notebook, co-writer, book,
  reading, attachments, generated files.
- `data/knowledge_bases`: local knowledge base files and indexes.
- `data/parse_cache`: parse cache through `PathService`.
- `data/users`: multi-user workspaces where enabled.
- `data/system`: auth/grants/secrets in multi-user/container setups.
- `data/pocketbase`: PocketBase sidecar data when used.
- `data/cli-apps`: installed CLI apps.

Smart Tutor persistence classification:

| Data | Type | Classification | Suggested Future Storage |
|---|---|---|---|
| User accounts/auth state | user/system | Must persist if auth enabled | Database/PocketBase/managed DB |
| Sessions/chat history | user | Must persist | SQLite on volume for small deployments; DB for production |
| Memory | user | Must persist | Volume or DB/object storage |
| Uploaded books/PDFs/docs | user content | Must persist | Object storage or volume for small deployments |
| Parsed document text | derived | Rebuildable but expensive | Persist cache on volume/object storage |
| RAG indexes/vector DBs | derived | Rebuildable but expensive | Volume for dev; managed/vector storage for scale |
| Embeddings | derived | Rebuildable but costly | Persist with index or DB |
| Learning progress | user | Must persist | DB |
| Quiz/test results | user | Must persist | DB |
| Generated reports/content | user/derived | Persist if user-facing | Object storage/volume |
| Temporary uploads during parsing | temporary | Temporary | Container temp dir, clean up |
| Logs | operational | Useful, not core data | stdout/stderr plus optional log storage |
| Ollama model files | local model data | Do not commit; not Railway | Local Ollama machine only |

Data that should not live only in ephemeral container filesystem:

- user uploads
- sessions
- memory
- learning progress
- quiz results
- long-lived generated content
- RAG indexes that should survive restarts
- provider/runtime settings

For Railway:

- Use a Railway volume only for small/development deployments.
- For production scale, investigate object storage for uploads and generated
  files, a managed database for sessions/progress/memory, and a managed vector
  or durable index strategy for RAG.
- Do not choose the final storage technology until Smart Tutor's production
  scale and user model are decided.

## 20. Railway WebSocket And Runtime Considerations

Smart Tutor relies on WebSocket streaming through `/api/v1/ws`.

Deployment considerations:

- Railway must support WebSocket upgrades for the backend service.
- Frontend proxy/rewrite rules must preserve WebSocket paths.
- Long-running tutor/RAG turns must not exceed Railway request/proxy limits.
- File uploads may be large; current WebSocket max size is computed from
  attachment settings. Production should validate upload limits explicitly.
- If multiple backend instances are used, sessions and active turn state may
  require sticky sessions or shared runtime coordination.
- Local disk state is currently process/container local unless mounted.
- Cron, EventBus, active turn runtime, and background tasks need graceful
  shutdown.

Scaling recommendation:

- Start Railway with one backend instance.
- Add horizontal scaling only after session/runtime state, storage, and active
  turn coordination are designed.

## 21. Deployment Safety Checklist

Before any future GitHub push or Railway deployment:

1. Run the full Python test suite.
2. Run frontend node tests.
3. Build the frontend.
4. Test backend startup.
5. Test frontend startup.
6. Test WebSocket chat.
7. Test OpenAI configuration.
8. Test local Ollama configuration.
9. Test RAG indexing and retrieval.
10. Test file upload and document preview.
11. Test memory.
12. Test learning progress and quiz results.
13. Test authentication if enabled.
14. Test accessibility, including keyboard-only and NVDA checks.
15. Test Linux/container compatibility.
16. Test production build.
17. Verify no secrets are present in working tree.
18. Verify no secrets are present in Git history.
19. Verify no absolute Windows paths are required.
20. Verify `.env` is ignored and `.env.example` contains no secrets.

Only after these checks should the project be pushed to
`FunctionSid/smart-tutor` and deployed to Railway.

## 22. CI/CD Investigation Recommendation

Do not create GitHub Actions yet.

Recommended future CI/CD design:

- Python tests with pytest.
- Python lint/format checks with Ruff/Black if the project keeps those tools.
- Frontend lint.
- Frontend type check.
- Frontend node tests.
- Frontend production build.
- i18n checks if localization remains.
- Secret scanning.
- Dependency/security checks.
- Docker build verification.
- Optional Playwright accessibility/smoke checks.
- Deployment-readiness workflow that runs before Railway deployment.

Suggested pipeline shape:

```text
Pull request
  |
  |-- backend tests/lint
  |-- frontend tests/lint/build
  |-- secret scan
  |-- Docker build check
  `-- deployment readiness report

main branch
  |
  `-- Railway deploy only after required checks pass
```

## 23. Required Changes Before First GitHub Push

- Confirm repository remote points to `https://github.com/FunctionSid/smart-tutor`
  when ready.
- Rebrand or clearly mark existing SmartTutor identity according to the chosen
  timing.
- Update `.env.example` for Smart Tutor variables without secrets.
- Verify `.gitignore` covers all generated/local/private data.
- Keep `data/`, local vector indexes, local uploads, `.env`, model files, and
  local databases out of Git.
- Run secret scanning.
- Run tests/builds.
- Remove accidental absolute developer paths from source and docs intended for
  deployment.
- Decide whether old SmartTutor-specific docs/assets remain in the first push.

## 24. Required Changes Before First Railway Deployment

- Decide one-service vs two-service Railway architecture.
- Ensure the exposed service listens on Railway `$PORT`.
- Configure OpenAI through Railway environment variables.
- Disable any requirement for Ollama in cloud deployment.
- Configure persistent storage.
- Configure production CORS and frontend/backend URLs.
- Verify WebSocket support.
- Verify health check.
- Verify Linux file permissions.
- Verify Next.js production build.
- Verify FastAPI startup/shutdown.
- Verify file uploads, RAG, memory, and sessions persist across restarts.
- Ensure no large model files or local vector stores are baked into the image.

## 25. Updated Verification Performed

Additional repository areas inspected for GitHub/Railway readiness:

- `.gitignore`
- `.dockerignore`
- `.env.example`
- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `compose.yaml`
- `smarttutor/runtime/home.py`
- `smarttutor/services/path_service.py`
- `smarttutor/services/setup/init.py`
- `smarttutor/services/storage/attachment_store.py`
- deployment/startup references in `scripts`, `web/next.config.js`, and
  `web/proxy.ts`
- persistence references across knowledge, reading, book, learning, memory,
  session, parsing, and RAG services

Updated conclusion:

- GitHub push is feasible after cleanup, secret scanning, `.env.example`
  updates, and tests.
- Railway deployment is feasible, but the current two-port all-in-one runtime
  needs an explicit Railway architecture decision.
- The biggest Railway risks are persistent storage, WebSocket behavior, upload
  limits, and `$PORT` alignment.
