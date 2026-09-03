# Smart Tutor — Master Blueprint & Live System Status

## Purpose

This document is the master technical blueprint, capability map, implementation status, and runtime verification record for Smart Tutor.

Smart Tutor is currently an agent-native learning application with a Next.js frontend, FastAPI backend, WebSocket/SSE streaming, configurable AI providers, document/knowledge-base ingestion, RAG retrieval, chat history, memory, notebooks, reading/library tools, voice endpoints, and guided learning features.

The intended product is an accessibility-first AI tutoring system where a learner can choose OpenAI or local Ollama, attach books and study material, build a searchable knowledge base, ask questions, learn interactively, practice, take quizzes/tests, revise weak areas, and track progress.

This document distinguishes implemented code from verified runtime behavior. A UI button alone is not proof that a feature works.

## Current Version

- Project directory: `D:\project\deep-tutor`
- Active package namespace: `smarttutor`
- Legacy namespace status: migration from `deeptutor` is in progress; many active Smart Tutor files are currently untracked in Git because the working tree is mid-rename.
- Frontend package: `web`
- Backend package: `smarttutor`

## Overall Status

🟡 IMPLEMENTED — NOT END-TO-END VERIFIED

Smart Tutor has substantial implemented architecture for chat, providers, settings, knowledge ingestion, embeddings, retrieval, memory, notebook, reader/library, and learning flows. OpenAI chat configuration and Ollama embedding connectivity were live-tested successfully during this audit. Full document ingestion into a real Class 10 Science knowledge base, RAG teaching from that document, duplicate re-upload proof, and NVDA manual testing remain ⚠️ UNVERIFIED.

## Last Audited

- Date: 2026-08-29
- Time zone: Asia/Calcutta
- Audit scope: source inspection, configuration inspection, startup script inspection, API map sampling, RAG/embedding/provider inspection, focused backend/frontend tests, live OpenAI diagnostic, live Ollama discovery, live embedding diagnostic, backend health check.

## How to Read This Document

Status labels:

- ✅ VERIFIED: actually tested during this audit or in current test runs.
- 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED: code exists and is wired, but the full user workflow was not live-tested.
- ⚠️ UNVERIFIED: behavior cannot currently be confirmed.
- ❌ NOT IMPLEMENTED: no implementation was found or the feature is only aspirational.

Never treat this document as a security vault. It must not contain API keys, tokens, passwords, or full secrets.

## Product Vision

```text
Student
  ↓
Open Smart Tutor
  ↓
Choose AI provider
  ↓
Choose AI model
  ↓
Attach textbook/study material
  ↓
Document ingestion
  ↓
Parsing
  ↓
Chunking
  ↓
Embedding
  ↓
Vector/index storage
  ↓
Knowledge retrieval
  ↓
AI Tutor
  ↓
Teach / Explain / Simplify / Summarize / Quiz / Practice / Test / Revise / Weak Topics / Progress
```

Current product reality:

- ✅ VERIFIED: OpenAI provider configuration resolves to `openai` + `gpt-4.1` and completed a Smart Tutor LLM diagnostic.
- ✅ VERIFIED: Ollama is reachable at audit time and model discovery returned installed local models.
- ✅ VERIFIED: embedding configuration uses Ollama `nomic-embed-text`; Smart Tutor embedding diagnostic returned a 768-dimensional vector.
- 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED: knowledge-base upload, parsing, chunking, embedding, index storage, progress, duplicate detection, and retrieval are implemented.
- ⚠️ UNVERIFIED: full Class 10 Science textbook upload, RAG answer grounding, duplicate re-upload behavior, and NVDA announcements.

## Capability Inventory

| Capability | Purpose | UI Location | Backend | Status | End-to-End Verified | Notes |
| ---------- | ------- | ----------- | ------- | ------ | ------------------- | ----- |
| Chat | General conversation and tutoring surface | `web/app/(workspace)/home/[[...sessionId]]/page.tsx` | `smarttutor/api/routers/unified_ws.py`, `smarttutor/runtime/orchestrator.py`, `smarttutor/capabilities/chat.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | OpenAI diagnostic passed, but full browser chat was not tested because frontend was not running on `localhost:3000`. |
| Tutor | Tutoring behavior through chat/capabilities | Chat/Home and learning surfaces | `smarttutor/capabilities`, `smarttutor/agents/chat` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Implemented as capability/tool behavior rather than one isolated tutor endpoint. |
| Teach me | Learning prompt/action | Chat UI quick actions and Book/Learning flows | Chat capability + RAG tools | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Not live-tested with a real indexed textbook. |
| Explain | Learning prompt/action | Chat UI | Chat capability | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Requires browser/RAG workflow verification. |
| Simplify | Learning prompt/action | Chat UI | Chat capability | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Requires browser/RAG workflow verification. |
| Summarize | Learning prompt/action | Chat UI | Chat capability and source tools | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Document grounding not live-tested. |
| Quiz | Generate or judge quiz questions | Chat, Playground, Book quiz blocks | `smarttutor/api/routers/question.py`, `smarttutor/api/routers/quiz_judge.py`, `smarttutor/book/blocks/quiz.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Node tests cover quiz helpers; full learner workflow not tested. |
| Test / Exam | Exam-style workflow | Chat/Playground/Book depending on flow | `smarttutor/api/routers/question.py`, quiz/book modules | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | No evidence of a complete formal exam system with marks/submission/weak-topic loop verified. |
| Practice | Practice through guided learning/quiz | Learning and chat | `smarttutor/learning`, `smarttutor/api/routers/mastery_path.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Backend mastery APIs exist; full workflow not tested. |
| Revise | Revision based on history/weak topics | Learning/chat | `smarttutor/learning`, memory and chat context | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Requires product-level workflow verification. |
| Weak topics | Identify weak knowledge points | Learning page | `smarttutor/learning/grading.py`, `smarttutor/learning/mastery.py`, `smarttutor/api/routers/mastery_path.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Deterministic grading/progress modules exist. |
| Suggestions | Suggest what to explore next | Dashboard/chat | `smarttutor/api/routers/dashboard.py`, `smarttutor/services/suggestions.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | API exists; live behavior not tested. |
| File upload | Add documents to a KB | `web/components/knowledge/KbDocumentsSection.tsx` | `POST /api/v1/knowledge/{kb_name}/upload` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Upload route and tests exist. |
| Document parsing | Convert PDFs/Office/text to text/images | Knowledge upload | `smarttutor/services/parsing`, `LlamaIndexDocumentLoader` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Shared parser bridge exists; real PDF test not run. |
| Text extraction | Extract markdown/text from parsed docs | Knowledge ingestion | `smarttutor/services/rag/pipelines/llamaindex/document_loader.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Implemented; not live-tested with supplied textbook. |
| Chunking | Split documents into nodes | Knowledge ingestion | `smarttutor/services/rag/pipelines/llamaindex/ingestion.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Uses LlamaIndex `SentenceSplitter`. |
| Embeddings | Make chunks searchable | Settings / Knowledge | `smarttutor/services/embedding` | ✅ VERIFIED | Yes, embedding diagnostic | `nomic-embed-text` via Ollama returned 768d. |
| Vector/index storage | Persist searchable index | Knowledge base directory | `smarttutor/services/rag/pipelines/llamaindex/storage.py`, `vector_store.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | FAISS when possible, SimpleVectorStore fallback. |
| Retrieval | Retrieve relevant chunks | RAG tool | `smarttutor/services/rag/service.py`, pipeline search | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Retrieval code exists; no real indexed textbook query was run. |
| RAG | Ground answers in KB content | Chat + selected KB | `smarttutor/tools/builtin` RAG tool, RAG service | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Needs full query evidence against an indexed document. |
| Source/context references | Show source metadata | Chat answer/tool results | LlamaIndex `_nodes_to_result()` source list | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Source fields include title, source path, page, chunk id, score. |
| Duplicate detection | Avoid re-indexing same bytes | Knowledge upload | `smarttutor/knowledge/add_documents.py` | ✅ VERIFIED | Unit verified | SHA-256 content hash, filename independent. |
| Existing-index reuse | Reuse compatible index versions | Knowledge/RAG storage | `index_versioning.py`, `storage.resolve_add_storage_plan()` | ✅ VERIFIED | Unit verified | Covered by focused backend tests; full PDF duplicate smoke not run. |
| Re-indexing | Rebuild index for current embedding config | Knowledge UI | `POST /api/v1/knowledge/{kb_name}/reindex` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Endpoint and code exist. |
| KB management | Create/list/delete/configure KBs | `/knowledge` | `smarttutor/knowledge/manager.py`, router | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Partial | Backend health verified; full UI not tested. |
| OpenAI | Cloud AI provider | Settings AI Models | `provider_runtime.py`, LLM provider | ✅ VERIFIED | Yes, diagnostic | Key configured locally; generation test passed. |
| Ollama | Local AI/embedding provider | Settings AI Models/Embedding | `local_provider.py`, embedding adapter | ✅ VERIFIED for discovery/embedding; ⚠️ chat unverified | Partial | Ollama reachable; local LLM generation not tested through Smart Tutor. |
| Dynamic Ollama discovery | List installed local models | Chat model selector/settings | `GET /api/v1/settings/llm-options?refresh_local=true`, `/fetch-models` | ✅ VERIFIED for service reachability; 🟡 UI not fully verified | Partial | Ollama `/api/tags` returned actual local models. |
| AI model selection | Choose chat/tutor model | `ModelSelector.tsx`, settings | `model_catalog.json`, `resolve_llm_runtime_config()` | ✅ VERIFIED for config resolution | Partial | Runtime resolves `gpt-4.1`; browser selection not clicked/tested. |
| Current model indicator | Show selected AI in chat | `web/components/chat/home/ModelSelector.tsx` | LLM options API | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Code has accessible visible indicator; not manually screen-reader tested. |
| Provider switching | Switch OpenAI/Ollama | Settings | Settings catalog APIs | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | No live provider switch test in browser. |
| Embedding separation | Keep embedding models out of chat selection | Settings/chat model code | Separate `llm` and `embedding` services in model catalog | ✅ VERIFIED by tests/config | Yes | Node and backend model selection tests passed. |
| Memory | Long-term memory/workbench | `/memory`, chat tools | `smarttutor/services/memory`, `smarttutor/api/routers/memory.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Rich API exists; not tested in this audit. |
| Voice | TTS/STT | Settings/voice controls | `smarttutor/api/routers/voice.py`, voice services | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Endpoints exist; no provider test run. |
| Notebook | Notes and records | `/notebook`, Space | `smarttutor/api/routers/notebook.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | API exists. |
| Download Markdown | Export chat | Chat UI | `web/lib/chat-export.ts` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Frontend helper exists. |
| Chat history | Persist sessions/messages | Chat/Space | `smarttutor/api/routers/sessions.py`, SQLite store | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Routes exist; not live-tested. |
| Personas | Configure personas | Settings/partners | `smarttutor/api/routers/personas.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | API exists. |
| Agents / Partners | IM-connected companions/subagents | Partners UI | `smarttutor/api/routers/partners.py`, `subagents.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Large subsystem present. |
| Settings | Configure providers/UI/features | `/settings/*` | `smarttutor/api/routers/settings.py` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Partial | Catalog diagnostics verified. |
| Library / Reader | Read documents with citations/annotations | `/reading`, Book/Reader | `smarttutor/api/routers/reading.py`, `smarttutor/reading` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Reader APIs exist; no manual test. |
| Keyboard navigation | Accessibility baseline | Frontend | Components use semantic controls | ⚠️ UNVERIFIED | No | Not tested manually. |
| NVDA compatibility | Screen reader compatibility | Frontend | ARIA/live regions in selected areas | ⚠️ UNVERIFIED | No | Must be manually tested with NVDA. |
| Live status announcements | Upload/process status | Knowledge upload panel | `ProgressTracker`, SSE, WebSocket, `role="status"` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Partial | Code/test verified; no NVDA run. |
| Accessible model selection | Announce model/provider | Chat model selector | `ModelSelector.tsx` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED | Needs screen-reader test. |
| Accessible exam interface | Exam accessibility | Quiz/test UI | Quiz components/routes | ⚠️ UNVERIFIED | No | Not audited deeply. |

## Architecture Overview

### Frontend

Purpose: browser UI for chat, knowledge bases, settings, library/book, memory, notebook, partners, playground, and admin.

Implementation: Next.js app under `web/app`, shared components under `web/components`, API client helpers under `web/lib`, hooks under `web/hooks`.

Important files:

- `web/app/(workspace)/home/[[...sessionId]]/page.tsx`
- `web/components/chat/home/ModelSelector.tsx`
- `web/components/chat/home/ChatComposer.tsx`
- `web/components/knowledge/KnowledgePage.tsx`
- `web/components/knowledge/KbDocumentsSection.tsx`
- `web/components/settings/ServiceConfigEditor.tsx`
- `web/lib/knowledge-api.ts`
- `web/lib/knowledge-helpers.ts`
- `web/hooks/useKnowledgeProgress.ts`

Dependencies: React, Next.js, TypeScript, lucide-react, i18next, local API proxy routes.

Current status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Verification: TypeScript passed; Node test runner passed; frontend was not running at `localhost:3000` during live check. Launcher advertises frontend port `3782`.

### Backend / API

Purpose: FastAPI service for chat, settings, knowledge, RAG, memory, notebook, voice, book, learning, partners, tools, and WebSockets.

Implementation: `smarttutor/api/main.py` includes routers.

Important files:

- `smarttutor/api/main.py`
- `smarttutor/api/routers/settings.py`
- `smarttutor/api/routers/knowledge.py`
- `smarttutor/api/routers/unified_ws.py`
- `smarttutor/api/routers/chat.py`
- `smarttutor/api/routers/sessions.py`
- `smarttutor/api/routers/mastery_path.py`
- `smarttutor/api/routers/memory.py`
- `smarttutor/runtime/orchestrator.py`

Dependencies: FastAPI, uvicorn, Pydantic, project services.

Current status: ✅ VERIFIED for backend health, 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED overall.

Verification: `GET http://127.0.0.1:8001/api/v1/knowledge/health` returned `status=ok`, config exists, base dir exists, zero registered KBs at audit time.

### Runtime Orchestration

Purpose: route each turn from CLI/API/SDK to a capability and stream events.

Implementation: `ChatOrchestrator` in `smarttutor/runtime/orchestrator.py` selects `context.active_capability` or defaults to `chat`, registers a `StreamBus`, runs capability, emits session/done/error events, and publishes completion events.

Current status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Verification: Source inspected; not live-tested through browser chat in this audit.

### Database / Persistence

Purpose: persist local runtime settings, knowledge bases, chat/session data, memory, notebooks, books, attachments, and task progress.

Implementation: local JSON/SQLite/file storage under `data/user` and `data/knowledge_bases`; optional PocketBase mirroring exists for some services.

Current status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Verification: settings and knowledge config files were inspected; no broad database migration/integrity test was run.

### Knowledge Base / Vector Search Layer

Purpose: ingest documents and retrieve relevant chunks.

Implementation:

- Manager: `smarttutor/knowledge/manager.py`
- Upload/add: `smarttutor/knowledge/add_documents.py`
- Initialize: `smarttutor/knowledge/initializer.py`
- Progress: `smarttutor/knowledge/progress_tracker.py`
- RAG factory/service: `smarttutor/services/rag/factory.py`, `service.py`
- LlamaIndex pipeline: `smarttutor/services/rag/pipelines/llamaindex`

Current status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Verification: duplicate detection and progress metadata unit tests passed; no real textbook KB exists in `data/knowledge_bases` at audit time.

### LLM Layer

Purpose: choose and call AI/tutor model.

Implementation:

- Runtime config: `smarttutor/services/config/provider_runtime.py`
- LLM config/client: `smarttutor/services/llm/config.py`, `client.py`
- Providers: `smarttutor/services/llm/provider_core`, `providers`
- Diagnostic runner: `smarttutor/services/config/test_runner.py`

Current status: ✅ VERIFIED for OpenAI diagnostic.

Verification: Smart Tutor LLM diagnostic completed successfully using OpenAI `gpt-4.1`.

### Embedding Layer

Purpose: convert chunks/questions into vectors for retrieval.

Implementation:

- Runtime config: `smarttutor/services/config/provider_runtime.py`
- Embedding config/client: `smarttutor/services/embedding/config.py`, `client.py`
- Adapters: `smarttutor/services/embedding/adapters`
- LlamaIndex adapter: `smarttutor/services/rag/pipelines/llamaindex/embedding_adapter.py`

Current status: ✅ VERIFIED for configured Ollama embedding.

Verification: Smart Tutor embedding diagnostic succeeded for Ollama `nomic-embed-text` and detected 768 dimensions.

### WebSocket / SSE Layer

Purpose: stream chat and background task progress.

Implementation:

- Chat WebSocket: `smarttutor/api/routers/unified_ws.py`, `chat.py`
- Knowledge task SSE: `GET /api/v1/knowledge/tasks/{task_id}/stream`
- Knowledge progress WebSocket: `GET/WS /api/v1/knowledge/{kb_name}/progress/ws`
- Frontend hook: `web/hooks/useKnowledgeProgress.ts`

Current status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Verification: Source inspected and tests passed; live browser behavior not tested.

## AI Provider Architecture

```text
                    Smart Tutor
                         │
                Provider Selection
                    /          \
                   /            \
              OpenAI           Ollama
                 │                │
                 ↓                ↓
          OpenAI model       Installed local model
                 │                │
                 └──────┬─────────┘
                        ↓
                    AI Response
```

Provider configuration lives in `data/user/settings/model_catalog.json`, separated by service kind: `llm`, `embedding`, `search`, `tts`, `stt`, `imagegen`, `videogen`.

Relevant files:

- `smarttutor/services/config/model_catalog.py`
- `smarttutor/services/config/provider_runtime.py`
- `smarttutor/services/model_selection/llm.py`
- `smarttutor/api/routers/settings.py`
- `web/lib/llm-options.ts`
- `web/hooks/useLLMOptions.ts`
- `web/components/settings/ServiceConfigEditor.tsx`
- `web/components/chat/home/ModelSelector.tsx`

Runtime resolution:

- Active LLM profile/model are resolved by `resolve_llm_runtime_config()`.
- Active embedding profile/model are resolved separately by `resolve_embedding_runtime_config()`.
- Local LLM providers treat `""`, `local`, `ollama`, and `none` as no-key sentinels and resolve to `sk-no-key-required`.
- The previous failure mode `401 Incorrect API key provided: local` is covered by tests.

Fallback behavior:

- Ollama discovery failure should surface as local provider unavailable; no verified evidence of silent OpenAI fallback for local chat during this audit.
- Retrieval with no compatible index returns a needs-reindex message instead of pretending to answer from a missing KB.

Security:

- API keys are stored in local runtime settings and redacted by settings APIs.
- The actual OpenAI key is not recorded in this document.

## OpenAI Status

- Provider: OpenAI
- Endpoint: `https://api.openai.com/v1`
- Configured: ✅ VERIFIED
- Selected model: `gpt-4.1`
- Key configured: YES
- Key validation: PASS
- Connection test: ✅ VERIFIED
- Actual generation test: ✅ VERIFIED
- RAG generation test: ⚠️ UNVERIFIED
- Security: The key is stored in local runtime settings; diagnostics redacted it; this document does not contain it.

Live diagnostic evidence:

```text
Resolved model `gpt-4.1` with binding `openai`.
Request target: https://api.openai.com/v1
Received LLM response.
LLM test completed successfully.
```

## Ollama Status

- Ollama URL: `http://localhost:11434`
- Reachability: ✅ VERIFIED
- Version: ⚠️ UNVERIFIED
- Dynamic discovery: ✅ VERIFIED via local `/api/tags`
- Selected chat model: ⚠️ UNVERIFIED in current config; OpenAI is currently selected for LLM.
- Chat generation test through Smart Tutor: ⚠️ UNVERIFIED
- Embedding generation through Smart Tutor: ✅ VERIFIED
- Error handling: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED

Installed local models found at audit time:

Chat/LLM-capable local models:

- `qwen3.5:27b`
- `qwen3:8b`
- `dolphin-mistral:latest`
- `qwen3:4b`
- `fauxpaslife/nanbeige4.1:latest`
- `qwen25-coder:latest`
- `qwen25-coder-14b:latest`
- `llama3:latest`

Embedding model:

- `nomic-embed-text:latest`

## Embedding Architecture

Embedding converts text chunks and user questions into numeric vectors. Smart Tutor uses embeddings to search a document index; the chat/tutor model uses retrieved text to produce answers.

```text
Smart Tutor
  ├─ AI/Tutor model: generates answers
  └─ Embedding model: makes documents searchable
```

- Embedding provider: Ollama
- Embedding model: `nomic-embed-text`
- Vector dimensions: ✅ VERIFIED as 768 by Smart Tutor embedding diagnostic.
- Configuration: `data/user/settings/model_catalog.json`, service `embedding`
- Runtime config: `smarttutor/services/embedding/config.py`
- Client: `smarttutor/services/embedding/client.py`
- Storage: LlamaIndex persisted storage under a KB version directory; FAISS binary store when available, otherwise LlamaIndex SimpleVectorStore.
- Index metadata: `meta.json`, `docstore.json`, `index_store.json`, vector store files, optional BM25 persistence.
- Chunk to embedding relationship: `SentenceSplitter` creates nodes; `Settings.embed_model` creates embeddings; `VectorStoreIndex` stores nodes/vectors.

Live diagnostic evidence:

```text
Resolved embedding model `nomic-embed-text` with binding `ollama`.
Request target: http://localhost:11434/api/embed
Probe returned 768d.
Embedding vector received.
EMBEDDING test completed successfully.
```

## Complete Document Ingestion Pipeline

```text
User uploads file to a knowledge base
        ↓
Upload received
        ↓
File validation
        ↓
Document identity/hash
        ↓
Duplicate check
        ↓
Existing?
   ┌────┴────┐
  YES        NO
   │          │
   │          ↓
   │       Parse
   │          ↓
   │       Extract text/images
   │          ↓
   │       Chunk
   │          ↓
   │       Embed
   │          ↓
   │       Store vectors/index
   │          ↓
   └────→ Document ready / KB ready
```

| Stage | What It Does | Code | Input | Output | Storage | Status | Verified |
| ----- | ------------ | ---- | ----- | ------ | ------- | ------ | -------- |
| Upload received | Accepts multipart files or archive extraction | `smarttutor/api/routers/knowledge.py` | Browser upload | Raw temp/staged files | KB raw folder | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED |
| File validation | Checks supported file routing and safe paths | `FileTypeRouter`, upload policy helpers | File paths | Routed file lists | None | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Partial |
| Content hash | Computes SHA-256 by bytes | `DocumentAdder._get_file_hash()` | File bytes | Hash string | `metadata.json:file_hashes` | ✅ VERIFIED | Unit verified |
| Duplicate check | Skips identical content already indexed | `DocumentAdder.add_documents()` | Hash + existing hashes | Staged files or skip summary | `metadata.json` | ✅ VERIFIED | Unit verified |
| Parse | Uses configured parser bridge | `LlamaIndexDocumentLoader._parse_document()` | PDF/Office/e-book | Markdown/text/images | Parser asset cache | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED |
| Text extraction | Converts parsed markdown/blocks to text | `LlamaIndexDocumentLoader` | Parsed document | LlamaIndex `Document` | In memory before index | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | ⚠️ UNVERIFIED |
| Chunking | Splits documents into nodes | `ingestion.build_ingestion_pipeline()` | LlamaIndex docs | Nodes | In index | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Test coverage exists |
| Embedding | Calls active embedding provider | `EmbeddingClient`, LlamaIndex embed adapter | Nodes/text | Vectors | Vector store | ✅ VERIFIED provider; ⚠️ full document unverified | Partial |
| Store vectors/index | Persists LlamaIndex index | `storage.create_index()`, `vector_store.py` | Nodes/vectors | Index files | KB version dir | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Unit coverage |
| Ready | Updates KB status/progress | `ProgressTracker`, `KnowledgeBaseManager` | Task result | Status `ready` | `kb_config.json` + `.progress.json` | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED | Unit coverage |

## File Upload Status / Progress

Expected status model:

```text
Validation
Staging
Indexing each file
Saving metadata
Complete or failed
```

Actual current backend events:

- `Validating {{count}} file(s)...`
- `Staged {{count}} new file(s)`
- `Staged {{count}} new file(s); skipped {{skipped}}`
- `Indexing {{name}}`
- `Indexed {{name}}`
- `Saving metadata...`
- `Successfully processed {{count}} files!`
- `No new files to process (all duplicates or invalid)`
- `Processing failed: {{error}}`

Important files:

- Backend upload task: `smarttutor/api/routers/knowledge.py`
- Progress tracker: `smarttutor/knowledge/progress_tracker.py`
- Task log stream: `smarttutor/api/utils/task_log_stream.py`
- Frontend progress hook: `web/hooks/useKnowledgeProgress.ts`
- Upload panel: `web/components/knowledge/KbDocumentsSection.tsx`
- Log UI: `web/components/common/ProcessLogs.tsx`

Status fields:

- `stage`
- `message`
- `message_key`
- `message_params`
- `current`
- `total`
- `percent` / `progress_percent`
- `indexed_count`
- `skipped_count`
- `duplicate_count`
- `index_changed`
- `index_action`
- `error`
- `error_code`
- `retryable`
- `task_id`

Accessible status:

- `KbDocumentsSection.tsx` exposes the current upload/index progress in a `role="status"` region with `aria-live="polite"` and `aria-atomic="true"`.
- 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED: code exists; no NVDA manual test was performed.

## Chunking

- Chunking engine: LlamaIndex `SentenceSplitter`
- Code: `smarttutor/services/rag/pipelines/llamaindex/ingestion.py`
- Default chunk size: `512`
- Default chunk overlap: `50`
- Config source: `smarttutor/services/rag/pipelines/llamaindex/config.py`, loaded from persisted LlamaIndex settings.
- UI/API config: `GET/PUT /api/v1/knowledge/rag-pipelines/llamaindex/config`
- Metadata: LlamaIndex node metadata includes file information from loader.
- Chunk IDs: LlamaIndex node IDs; exact ID generation is managed by LlamaIndex. ⚠️ UNVERIFIED beyond source inspection.
- Storage: persisted into LlamaIndex docstore/vector store under KB version directory.

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

## Embedding Storage / Vector Database

Vector storage technology:

- LlamaIndex `VectorStoreIndex`
- FAISS-backed store when all node embeddings share one dimension and FAISS support is available.
- LlamaIndex SimpleVectorStore fallback when FAISS cannot be used.

Important files:

- `smarttutor/services/rag/pipelines/llamaindex/storage.py`
- `smarttutor/services/rag/pipelines/llamaindex/vector_store.py`
- `smarttutor/services/rag/index_versioning.py`

Persistence location:

```text
data/knowledge_bases/<kb-name>/
  raw/
  metadata.json
  version-N/
    meta.json
    docstore.json
    index_store.json
    default__vector_store.json or FAISS-backed vector store file
    bm25/ or equivalent persisted BM25 directory when available
```

Search mechanism:

```text
user question
 ↓
question embedding by active embedding model
 ↓
LlamaIndex retriever
 ↓
hybrid retrieval if BM25 package available, otherwise vector retrieval
 ↓
top relevant chunks
 ↓
RAG tool result
 ↓
chat capability uses result as context
```

Top-K:

- Default `top_k`: `5`
- Config: LlamaIndex RAG settings via `default_top_k()`

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

## RAG Pipeline

```text
Question
 ↓
Chat/capability decides to use RAG tool
 ↓
RAGService resolves KB provider
 ↓
LlamaIndex pipeline resolves active embedding signature
 ↓
Matching index version loaded
 ↓
Retriever returns top-K nodes
 ↓
Result content + sources returned to capability
 ↓
Selected AI model generates final answer
```

Important files:

- `smarttutor/services/rag/service.py`
- `smarttutor/services/rag/factory.py`
- `smarttutor/services/rag/pipelines/llamaindex/pipeline.py`
- `smarttutor/services/rag/pipelines/llamaindex/retrievers.py`
- `smarttutor/tools/builtin/__init__.py`
- `smarttutor/capabilities/chat.py`

Fallback behavior:

- If no compatible index is found, LlamaIndex search returns a message that the KB has no index for the active embedding model and sets `needs_reindex=True`.
- If retrieval returns nodes, `_nodes_to_result()` returns `answer`, `content`, and `sources`.

Whether final answers are strictly source-only:

- ⚠️ UNVERIFIED. The retrieval tool returns source content, but this audit did not prove the final chat prompt forbids unsupported general model knowledge in every learning action.

## Source Grounding

LlamaIndex source payload includes:

- `title`
- `content` preview
- `source`
- `page`
- `chunk_id`
- `score`

Code: `smarttutor/services/rag/pipelines/llamaindex/pipeline.py`, `_nodes_to_result()`.

User-visible citation/source behavior: ⚠️ UNVERIFIED in browser.

## Duplicate Document Handling

Implementation:

- SHA-256 is computed over file bytes in `DocumentAdder._get_file_hash()`.
- Successful indexing records `metadata.json:file_hashes` keyed by path relative to `raw/`.
- Later uploads compare the new content hash against all ingested hash values.
- Identical content is skipped even if the filename changed.
- Same filename with different content is staged using a non-colliding filename such as `README (2).md`.
- Upload task now records `skipped_count` and `duplicate_count` in progress metadata.

First upload:

```text
file bytes
 ↓
content hash
 ↓
stage
 ↓
parse/chunk/embed/index
 ↓
record hash
```

Second identical upload:

```text
file bytes
 ↓
same content hash
 ↓
duplicate detected
 ↓
skip staging/indexing
 ↓
existing index remains ready
```

Verified behavior:

- ✅ Unit verified: duplicate content is detected by hash.
- ✅ Unit verified: missing/invalid files and duplicate files are counted.
- ✅ Unit verified: progress tracker persists skip metadata in the latest snapshot and stores stable last upload counts on the KB entry.

Unverified behavior:

- ⚠️ Full duplicate PDF upload through browser.
- ⚠️ Proof that no provider-level embedding call occurs during duplicate browser upload. The code path skips before indexing, but this was not measured live.

Special cases:

- File contents change: new hash, file is staged and indexed.
- Filename changes but contents identical: duplicate skip.
- Embedding model changes: index signature changes; matching version lookup may require re-index or reuse a prior matching version.
- Index deleted/corrupted: provider index validation/re-index paths exist; full recovery was not live-tested.

## Learning Features

| Feature | UI | Backend | Prompt/Logic | Uses RAG | Uses Selected Model | Stores Result | Progress Integration | Status |
| ------- | -- | ------- | ------------ | -------- | ------------------- | ------------- | -------------------- | ------ |
| Teach me | Chat / Learning | Chat capability, RAG tools, mastery path | Capability prompts/tools | 🟡 likely when KB selected | 🟡 via LLM runtime | Chat/session | StreamBus | ⚠️ UNVERIFIED |
| Explain | Chat | Chat capability | Prompt/action | 🟡 likely when KB selected | 🟡 via LLM runtime | Chat/session | StreamBus | ⚠️ UNVERIFIED |
| Simplify | Chat | Chat capability | Prompt/action | 🟡 likely when KB selected | 🟡 via LLM runtime | Chat/session | StreamBus | ⚠️ UNVERIFIED |
| Summarize | Chat / source tools | Chat capability, read_source/RAG | Prompt/action | 🟡 likely | 🟡 via LLM runtime | Chat/session | StreamBus | ⚠️ UNVERIFIED |
| Quiz | Chat/Book/Question APIs | `question.py`, `quiz_judge.py`, book quiz block | Question generation/judging | 🟡 likely when KB selected | 🟡 via LLM runtime | Session/book quiz attempts | WebSocket | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED |
| Test | Playground/Chat | Question generation APIs | Mimic/generate/judge paths | ⚠️ unknown | 🟡 via LLM runtime | Some quiz/session records | WebSocket | ⚠️ UNVERIFIED |
| Practice | Learning page/chat | `mastery_path.py`, `learning` modules | Mastery policy/grading | ⚠️ unknown | 🟡 via LLM runtime | Mastery progress | APIs | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED |
| Revise | Learning/chat | Memory/learning/chat | Not fully traced | ⚠️ unknown | 🟡 via LLM runtime | Progress/memory possibly | ⚠️ unknown | ⚠️ UNVERIFIED |
| Weak topics | Learning | `learning/grading.py`, `learning/mastery.py` | Deterministic grading + progress | ⚠️ unknown | N/A or LLM-assisted | Mastery store | APIs | 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED |

## Exam System

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED, with gaps.

Evidence found:

- Question generation WebSockets: `smarttutor/api/routers/question.py`
- Quiz judging WebSocket: `smarttutor/api/routers/quiz_judge.py`
- Book quiz attempts: `smarttutor/api/routers/book.py`
- Question notebook APIs: `smarttutor/api/routers/question_notebook.py`

Not verified:

- Complete exam generation from syllabus/source.
- Marks and difficulty controls as a coherent student exam workflow.
- Student submission to automatic marking to explanations to score to weak-topic update.
- RAG grounding for exam generation.

Do not call the exam system complete until a full workflow is demonstrated.

## Memory

Purpose: preserve learner/session facts and provide a memory workbench.

Implementation:

- APIs: `smarttutor/api/routers/memory.py`
- Storage paths: `smarttutor/services/memory/paths.py`
- Document model/ops: `smarttutor/services/memory/document.py`, `ops.py`
- Modes: update, audit, dedup, merge under `smarttutor/services/memory/consolidator`

Storage:

```text
data/user/workspace/memory/
  L2/
  L3/
  trace/
  backup/
```

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Privacy/security: local files; delete/reset/apply APIs exist. Full privacy audit not performed.

## Voice

Purpose: speech-to-text and text-to-speech.

Implementation:

- API: `smarttutor/api/routers/voice.py`
- Config/services: `smarttutor/services/voice`
- Settings: model catalog services `tts` and `stt`

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Verification: no live STT/TTS provider test was run during this audit.

## Accessibility

Implemented or observed in code:

- Chat and settings components use standard buttons/selects in many places.
- Knowledge upload status has a live `role="status"` region with `aria-live="polite"` and `aria-atomic="true"`.
- Chat model indicator was implemented as visible/accessibility-aware UI in `ModelSelector.tsx`.
- Process logs are visible in a `<details>` region.

Tested automatically:

- TypeScript compile.
- ESLint.
- Node helper/component-adjacent tests.

Tested manually:

- ❌ No NVDA manual test was performed during this audit.
- ❌ No full keyboard-only pass was performed during this audit.

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

## Settings Architecture

Actual settings areas include:

| Setting Area | Purpose | Normal User Visibility | Advanced/Developer | Backend | Status |
| ------------ | ------- | ---------------------- | ------------------ | ------- | ------ |
| Appearance | Theme/UI preferences | Yes | No | `settings.py`, UI settings | 🟡 IMPLEMENTED |
| AI / Tutor Model | LLM provider/model/key | Yes | Some advanced profile fields still exist | `model_catalog.json`, settings router | ✅ OpenAI verified; UI unverified |
| Embedding Model | RAG embedding provider/model | Should be separate from chat | Advanced concepts visible | `model_catalog.json` | ✅ Ollama embedding verified |
| Knowledge Base | RAG providers, document upload, index versions | Yes | Engine configs are advanced | `knowledge.py` | 🟡 IMPLEMENTED |
| Chat | Attachments, starters, model selector | Yes | Network/backend details should be hidden | settings/chat routes | 🟡 IMPLEMENTED |
| Voice | TTS/STT | Yes | Provider setup | voice router/catalog | ⚠️ UNVERIFIED |
| Memory | Memory settings/workbench | Yes | Workbench is advanced | memory router | ⚠️ UNVERIFIED |
| Network/System | Ports/backend URL/timeouts | Prefer Advanced/Developer | Yes | system/settings | ⚠️ UNVERIFIED |

Intended simple structure:

```text
Appearance
AI Models
Knowledge Base
Chat
Voice
Memory
```

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED. A UI simplification audit remains needed to confirm backend/API URLs are not prominent for normal students.

## Security

Rules:

- Never record real API keys in Markdown.
- Never hard-code keys in source.
- Never expose keys to frontend JavaScript.
- Never log complete keys.
- Never add secrets to tests/fixtures.

Current findings:

- Model catalog APIs redact secret fields via `smarttutor/services/config/model_catalog.py`.
- OpenAI key was configured locally in `data/user/settings/model_catalog.json`.
- Diagnostic output redacted the key.
- Root `.env` is absent and not required by the current project behavior.
- The repository is dirty/mid-migration; Git ignore behavior was not fully audited.

Status: ✅ VERIFIED for this document not containing the key; broader secret scanning should be run before commit/release.

## Startup / Installation

Scripts:

- `start-smart-tutor.bat`
  - Changes to project root.
  - Requires `.venv\Scripts\activate.bat`.
  - Activates venv.
  - Installs Smart Tutor editable with `python -m pip install -e .` if `smarttutor` is not available.
  - Runs `npm ci --legacy-peer-deps` in `web` if `web\node_modules` is missing.
  - Opens browser to `http://localhost:3782` after an 8-second delay.
  - Runs `smarttutor start --dev`.
- `set-openai-key.bat`
  - Calls `set-openai-key.ps1`.
- `set-openai-key.ps1`
  - Securely prompts for an OpenAI API key.
  - Writes the LLM profile to `data/user/settings/model_catalog.json`.
  - Does not print the key back.

Ports:

- Backend shown by launcher: `http://localhost:8001`
- Frontend shown by launcher: `http://localhost:3782`
- Live audit backend health used: `http://127.0.0.1:8001`
- Live audit frontend check at `localhost:3000`: failed because nothing was listening there.

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED. Launcher script exists; full startup from a fresh terminal was not run in this audit.

## Database / Persistence Map

```text
Configuration
  ↓
data/user/settings/*.json
data/user/settings/model_catalog.json

Knowledge base registry
  ↓
data/knowledge_bases/kb_config.json

Knowledge documents
  ↓
data/knowledge_bases/<kb-name>/raw/

Knowledge metadata and duplicate hashes
  ↓
data/knowledge_bases/<kb-name>/metadata.json

Indexes / chunks / embeddings
  ↓
data/knowledge_bases/<kb-name>/version-N/
docstore.json, index_store.json, vector store files, meta.json

Progress
  ↓
data/knowledge_bases/<kb-name>/.progress.json
data/knowledge_bases/kb_config.json progress/last_* fields

Chat attachments
  ↓
data/user/workspace/chat/attachments/

Chat history / sessions
  ↓
SQLite store via `smarttutor/services/session`
exact file path ⚠️ UNVERIFIED in this audit

Memory
  ↓
data/user/workspace/memory/

Cron jobs
  ↓
data/user/workspace/cron/jobs.json

Notebook / question notebook / book data
  ↓
Project services under `smarttutor/services/notebook`, `question_notebook`, `book`
exact file/database paths ⚠️ UNVERIFIED in this audit
```

## API Map

| Endpoint | Method | Purpose | Frontend Caller | Status | Tested |
| -------- | ------ | ------- | --------------- | ------ | ------ |
| `/api/v1/ws` | WebSocket | Unified chat/capability stream | Chat page/context | 🟡 IMPLEMENTED | ⚠️ No live browser test |
| `/api/v1/chat` | WebSocket | Legacy/chat WebSocket | Chat clients | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/chat/sessions` | GET | List chat sessions | Chat history | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/sessions` | GET | List persisted sessions | Chat/Space | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/settings` | GET | Load settings | Settings UI | 🟡 IMPLEMENTED | Partial |
| `/api/v1/settings/catalog` | GET/PUT | Read/write model catalog | Settings UI | ✅ VERIFIED indirectly | Tests/diagnostics |
| `/api/v1/settings/llm-options` | GET | Chat model options, local refresh | Model selector | ✅ VERIFIED by tests | Node/backend tests |
| `/api/v1/settings/fetch-models` | POST | Discover provider models | Settings UI | ✅ VERIFIED by tests | Backend tests |
| `/api/v1/settings/tests/{service}/start` | POST | Start provider diagnostic | Settings UI | ✅ VERIFIED for llm/embedding | Live diagnostic |
| `/api/v1/settings/tests/{service}/{run_id}/events` | GET | Diagnostic events | Settings UI | ✅ VERIFIED indirectly | Live diagnostic object inspected |
| `/api/v1/knowledge/health` | GET | Knowledge subsystem health | Debug/settings | ✅ VERIFIED | Live HTTP check |
| `/api/v1/knowledge/list` | GET | List KBs | Knowledge/chat | ✅ VERIFIED route exists; live returned count via health | Partial |
| `/api/v1/knowledge/create` | POST | Create KB and initial index | Knowledge UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/knowledge/{kb_name}/upload` | POST | Upload/add docs | Knowledge UI | 🟡 IMPLEMENTED | Unit tests only |
| `/api/v1/knowledge/tasks/{task_id}/stream` | GET | SSE task logs | `useKnowledgeProgress` | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED live |
| `/api/v1/knowledge/{kb_name}/progress/ws` | WebSocket | Progress updates | `useKnowledgeProgress` | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED live |
| `/api/v1/knowledge/{kb_name}/progress` | GET | Latest progress | Knowledge UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED live |
| `/api/v1/knowledge/{kb_name}/reindex` | POST | Rebuild index | Knowledge UI | 🟡 IMPLEMENTED | Unit/focused tests only |
| `/api/v1/knowledge/{kb_name}/retry` | POST | Retry failed indexing | Knowledge UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/knowledge/rag-pipelines/llamaindex/config` | GET/PUT | RAG chunk/retrieval settings | Knowledge settings | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/knowledge/rag-pipelines/model-options` | GET | RAG model options | Knowledge settings | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/reading/materials` | GET/POST | Reader materials | Library/reader | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/mastery-path/progress` | GET | Mastery progress | Learning page | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/question/generate` | WebSocket | Question generation | Playground/quiz | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/question/judge` | WebSocket | Quiz judging | Quiz UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/memory/overview` | GET | Memory overview | Memory UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/notebook/list` | GET | Notebook list | Notebook UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/voice/tts` | POST | Text-to-speech | Voice UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |
| `/api/v1/voice/stt` | POST | Speech-to-text | Voice UI | 🟡 IMPLEMENTED | ⚠️ UNVERIFIED |

## Frontend Component Map

| Component/Page | Purpose | Backend/API | Status |
| -------------- | ------- | ----------- | ------ |
| `web/app/(workspace)/home/[[...sessionId]]/page.tsx` | Main chat/tutor page | `/api/v1/ws`, settings, sessions, knowledge | 🟡 IMPLEMENTED |
| `web/components/chat/home/ModelSelector.tsx` | Select/show AI model | `/api/v1/settings/llm-options` | 🟡 IMPLEMENTED |
| `web/components/chat/home/ChatComposer.tsx` | Prompt/files/tools input | Unified WS | 🟡 IMPLEMENTED |
| `web/components/chat/home/ChatMessages.tsx` | Render transcript | Sessions/chat events | 🟡 IMPLEMENTED |
| `web/components/knowledge/KnowledgePage.tsx` | Knowledge base shell | Knowledge APIs | 🟡 IMPLEMENTED |
| `web/components/knowledge/KnowledgeHome.tsx` | KB overview/provider cards | Knowledge APIs | 🟡 IMPLEMENTED |
| `web/components/knowledge/KbDocumentsSection.tsx` | Upload docs and show progress | Upload/SSE/WS | 🟡 IMPLEMENTED |
| `web/components/knowledge/KbIndexVersionsSection.tsx` | Show/retry index versions | Knowledge APIs | 🟡 IMPLEMENTED |
| `web/components/settings/ServiceConfigEditor.tsx` | Provider/model config | Settings catalog APIs | 🟡 IMPLEMENTED |
| `web/app/(utility)/settings/llm/page.tsx` | AI/Tutor model settings | Settings catalog | 🟡 IMPLEMENTED |
| `web/app/(utility)/settings/embedding/page.tsx` | Embedding model settings | Settings catalog | 🟡 IMPLEMENTED |
| `web/app/(utility)/space/learning/page.tsx` | Mastery path UI | Mastery APIs | 🟡 IMPLEMENTED |
| `web/app/(workspace)/book/page.tsx` | Book/learning content UI | Book APIs/WS | 🟡 IMPLEMENTED |
| `web/app/(utility)/notebook/page.tsx` | Notebook UI | Notebook APIs | 🟡 IMPLEMENTED |
| `web/app/(utility)/memory/l1/page.tsx` | Memory workbench | Memory APIs | 🟡 IMPLEMENTED |

## Backend Component Map

| Module | Purpose | Dependencies | Status |
| ------ | ------- | ------------ | ------ |
| `smarttutor/runtime/orchestrator.py` | Capability routing and stream lifecycle | StreamBus, registries | 🟡 IMPLEMENTED |
| `smarttutor/runtime/launcher.py` | Backend/frontend launch lifecycle | uvicorn, Node/Next | 🟡 IMPLEMENTED |
| `smarttutor/api/main.py` | FastAPI app/router assembly | routers/services | ✅ Health verified |
| `smarttutor/api/routers/settings.py` | Settings/catalog/provider diagnostics | config services | ✅ Diagnostics verified |
| `smarttutor/api/routers/knowledge.py` | KB CRUD/upload/progress/config | knowledge/RAG services | 🟡 IMPLEMENTED |
| `smarttutor/knowledge/add_documents.py` | Incremental document staging/indexing | RAGService, hashes | ✅ Focus tests |
| `smarttutor/knowledge/manager.py` | KB registry/status/metadata | JSON config, optional PocketBase | ✅ Focus tests |
| `smarttutor/knowledge/progress_tracker.py` | Progress persistence/broadcast | manager, broadcaster | ✅ Focus tests |
| `smarttutor/services/rag/service.py` | RAG provider facade | RAG factory/pipelines | 🟡 IMPLEMENTED |
| `smarttutor/services/rag/pipelines/llamaindex` | Default local RAG pipeline | LlamaIndex, embeddings | 🟡 IMPLEMENTED |
| `smarttutor/services/embedding` | Embedding config/client/adapters | provider runtime, Ollama/OpenAI/etc. | ✅ Ollama verified |
| `smarttutor/services/llm` | LLM config/providers/client | OpenAI SDK, local/cloud providers | ✅ OpenAI verified |
| `smarttutor/services/session` | Chat/session persistence | SQLite/PocketBase paths | 🟡 IMPLEMENTED |
| `smarttutor/services/memory` | Memory documents/workbench | filesystem, LLM | 🟡 IMPLEMENTED |
| `smarttutor/learning` | Mastery model/policy/grading | Pydantic, APIs | 🟡 IMPLEMENTED |
| `smarttutor/book` | Book creation/blocks/progress | LLM, notebook, sessions | 🟡 IMPLEMENTED |

## Test Inventory

Current test results run during this audit session:

```text
Backend focused pytest:
115 passed in 2.98s

Knowledge-focused pytest:
22 passed in 1.55s

Node tests:
589 passed

TypeScript:
PASS (`npx tsc --noEmit`)

Lint:
PASS — 0 errors, 52 warnings

OpenAI diagnostic:
PASS — Smart Tutor LLM test completed successfully

Embedding diagnostic:
PASS — Smart Tutor embedding test completed successfully; 768d vector

Ollama discovery:
PASS — `/api/tags` returned installed models

Backend health:
PASS — knowledge health returned `status=ok`

Frontend live check:
FAIL/UNVERIFIED — nothing was listening at `localhost:3000`; launcher uses port `3782`

Full build:
⚠️ UNVERIFIED — not run in this audit

Class 10 document ingestion/RAG duplicate smoke:
⚠️ UNVERIFIED — not run with user-provided textbook
```

Focused backend command:

```text
.venv\Scripts\python.exe -m pytest tests\services\config\test_provider_runtime.py tests\services\model_selection\test_llm_selection.py tests\api\test_settings_router.py tests\knowledge\test_add_documents_linked_folder.py tests\knowledge\test_progress_tracker.py tests\knowledge\test_document_adder_provider.py tests\api\test_upload_off_event_loop.py -q
```

Node command:

```text
npm run test:node -- knowledge-helpers llm-options-transport
```

## Live Runtime Verification

### Test A — OpenAI

```text
OpenAI selected
 ↓
gpt-4.1
 ↓
Smart Tutor LLM diagnostic
 ↓
PASS
```

Result: ✅ VERIFIED.

### Test B — Ollama

```text
Ollama reachable
 ↓
models discovered
 ↓
PASS
```

Result: ✅ VERIFIED for discovery. ⚠️ UNVERIFIED for Smart Tutor local chat generation because LLM is currently configured for OpenAI and no browser/provider-switch chat test was run.

### Test C — Embeddings

```text
nomic-embed-text
 ↓
Smart Tutor embedding diagnostic
 ↓
768d vector
 ↓
PASS
```

Result: ✅ VERIFIED.

### Test D — Document Ingestion

```text
upload
 ↓
parse
 ↓
chunk
 ↓
embed
 ↓
index
 ↓
ready
```

Result: ⚠️ UNVERIFIED. No Class 10 Science textbook was uploaded through the KB UI during this audit. `data/knowledge_bases` had zero registered KBs at the backend health check.

### Test E — RAG

Result: ⚠️ UNVERIFIED. No indexed textbook was queried during this audit.

### Test F — Duplicate

Result: ✅ VERIFIED by unit tests for content-hash staging skip. ⚠️ UNVERIFIED as full browser/PDF duplicate workflow.

## Known Problems

### Problem: Full document-to-RAG product workflow is not verified

Impact: Smart Tutor cannot yet be honestly called complete for the “attach textbook and start learning” acceptance criterion.

Reproduction: Create/upload a real Class 10 Science PDF, wait for ingestion, ask document-specific questions, upload same PDF again.

Root cause: No live full workflow was run during this audit.

Status: ⚠️ UNVERIFIED.

Recommended fix: Run a controlled Class 10 textbook ingestion/RAG/duplicate smoke test and record exact evidence.

### Problem: Frontend was not running at `localhost:3000`

Impact: Browser chat/settings/knowledge UI could not be live-tested at that URL.

Reproduction: `Invoke-WebRequest http://localhost:3000` failed with connection refused.

Root cause: App launcher advertises frontend `http://localhost:3782`; port `3000` is not the active frontend in this setup.

Status: ⚠️ UNVERIFIED for frontend runtime.

Recommended fix: Start via `start-smart-tutor.bat` or `smarttutor start --dev`, then verify `http://localhost:3782`.

### Problem: NVDA compatibility not manually tested

Impact: Accessibility claims must remain limited to implemented ARIA/live-region code.

Reproduction: Run upload/model-selection workflows with NVDA.

Root cause: No NVDA session was available during this audit.

Status: ⚠️ UNVERIFIED.

Recommended fix: Perform manual NVDA test for upload progress, completion, model selector, chat streaming, quiz/test surfaces.

### Problem: Working tree is mid-migration and very dirty

Impact: It is harder to separate intended Smart Tutor files from old DeepTutor paths and unrelated changes.

Reproduction: `git status --short` shows many changed/deleted/untracked files.

Root cause: Ongoing rename/migration.

Status: 🟡 IMPLEMENTED — NOT END-TO-END VERIFIED.

Recommended fix: Complete migration cleanup and commit in coherent checkpoints after secret scan.

## Remaining Work

### Critical

- Run full startup using `start-smart-tutor.bat` and verify frontend at `http://localhost:3782`.
- Upload a real Class 10 Science textbook into a KB.
- Verify parse, chunk, embed, index, ready state, and source metadata.
- Ask document-specific Teach/Explain/Summarize/Quiz/Test/Practice/Revise prompts and verify retrieved source content is used.
- Upload the exact same textbook again and prove duplicate processing skips re-embedding/re-indexing.
- Manually test NVDA announcements for model selection and upload progress.
- Run a broad secret scan before any commit or handoff.

### Important

- Simplify normal Settings navigation to the intended student-facing sections.
- Move backend/network/port details into Advanced/Developer if still prominent.
- Add automated integration tests for upload progress events and duplicate no-embedding behavior.
- Add a small fixture-based RAG integration test that indexes a tiny document and queries it.
- Verify Ollama chat generation through Smart Tutor after selecting a local LLM.
- Verify source citations in the browser.

### Nice to Have

- Add a living audit command that regenerates parts of this document.
- Add a one-click “system readiness” screen for OpenAI, Ollama, embedding, parser, and KB health.
- Add scripted accessibility smoke checks where possible.

## Definition of Done

- [ ] Smart Tutor starts reliably
- [x] OpenAI works
- [x] Ollama discovery works
- [ ] Ollama chat works through Smart Tutor
- [x] Ollama models dynamically discovered
- [x] Chat model runtime resolution works for current OpenAI selection
- [x] Current model visible in code/UI implementation
- [x] Embedding model separate
- [x] `nomic-embed-text` works
- [ ] File parsing works for user textbook
- [ ] Chunking works for user textbook
- [x] Embedding provider generates vectors
- [ ] Vectors/index stored for user textbook
- [x] Ingestion progress implemented
- [x] Ingestion progress accessible in code
- [ ] Document-ready announcement manually verified
- [ ] RAG retrieval works for user textbook
- [ ] Source grounding works in browser
- [x] Duplicate detection works by content hash
- [x] Existing index reuse implemented/test-covered
- [ ] Teach works with uploaded textbook
- [ ] Explain works with uploaded textbook
- [ ] Quiz works with uploaded textbook
- [ ] Practice works with uploaded textbook
- [ ] Test/exam works with uploaded textbook
- [ ] Revision works with uploaded textbook
- [ ] Weak topics works with uploaded textbook
- [ ] Progress works end-to-end
- [ ] NVDA tested
- [ ] Security verified with full secret scan
- [ ] Startup verified end-to-end
- [x] Focused relevant tests pass
- [ ] Full relevant test/build suite passes

## Audit Rules

This document must never claim functionality based solely on the presence of UI controls or source code.

A feature is:

✅ VERIFIED
only when it has been actually tested.

🟡 IMPLEMENTED — NOT END-TO-END VERIFIED
when implementation exists but real runtime testing has not been completed.

⚠️ UNVERIFIED
when the implementation or behavior cannot currently be confirmed.

❌ NOT IMPLEMENTED
when the capability does not currently exist.

All test results must be current.

Never record API keys, passwords, tokens, or other secrets.

When updating this document, preserve previous important findings but update stale status information.

Last audit date and audit scope must always be recorded.
