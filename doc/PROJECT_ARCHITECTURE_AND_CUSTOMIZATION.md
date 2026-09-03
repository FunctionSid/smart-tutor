# SmartTutor Project Architecture And Customization Guide

This document explains what this project does, how it is organized, what
technologies it uses, and which parts can be kept, changed, or removed when
turning it into a new project.

The goal is to make the codebase easier for a human developer or another AI
agent to understand before making changes.

## 1. What This Project Is

SmartTutor is an agent-native AI learning platform. It is not only a chat UI.
It is a complete application with:

- A Python backend/runtime.
- A command-line interface.
- A Next.js web frontend.
- A WebSocket streaming API.
- A plugin-style architecture for AI capabilities and tools.
- Knowledge base and RAG support.
- Memory, notebooks, question banks, partners, skills, and document parsing.

The main product idea is an intelligent learning companion that can tutor,
solve problems, research, generate questions, visualize concepts, build books,
read documents, and remember user context.

## 2. High-Level Architecture

The system has three major entry points:

- CLI: `smarttutor` command from `smarttutor_cli/main.py`.
- Web API: FastAPI backend in `smarttutor/api`.
- Web frontend: Next.js app in `web`.

All entry points eventually route user work through a shared runtime:

```text
User
  |
  |-- CLI: smarttutor run chat "..."
  |-- Web UI: browser chat page
  |-- SDK/internal app facade
  |
  v
Turn request / UnifiedContext
  |
  v
ChatOrchestrator
  |
  |-- chooses capability: chat, deep_solve, deep_research, visualize, etc.
  |-- gives capability access to tools
  |-- streams events through StreamBus
  |
  v
Capability pipeline
  |
  |-- may call LLM
  |-- may call tools
  |-- may retrieve from knowledge base
  |-- may write memory or notes
  |
  v
Streamed result back to CLI / WebSocket / UI
```

The most important backend file is:

- `smarttutor/runtime/orchestrator.py`

The orchestrator selects and runs a capability. If no capability is selected,
it uses `chat`.

## 3. Core Concepts

### 3.1 UnifiedContext

Location:

- `smarttutor/core/context.py`

This is the common request object used by the runtime. It holds the user
message, session id, selected capability, enabled tools, knowledge bases,
language, config, metadata, and references.

If you build a new project, this is one of the core files to keep.

### 3.2 ChatOrchestrator

Location:

- `smarttutor/runtime/orchestrator.py`

This is the central router. It:

- Creates a session id when needed.
- Chooses the active capability.
- Creates a `StreamBus`.
- Runs the selected capability.
- Streams events back to the caller.
- Publishes completion events.

This should be kept if you want the existing agent architecture.

### 3.3 Capabilities

Locations:

- `smarttutor/runtime/bootstrap/builtin_capabilities.py`
- `smarttutor/capabilities`
- `smarttutor/agents`

A capability is a larger workflow that owns a full user turn. Examples:

- `chat`: normal agentic chat.
- `deep_solve`: step-by-step solving.
- `deep_question`: question generation.
- `deep_research`: research pipeline.
- `visualize`: creates visualizations.
- `math_animator`: Manim-based math animation.
- `mastery_path`: guided learning and mastery practice.
- `immersive_reading`: document reading workflow.

Capabilities are registered by class path in:

- `smarttutor/runtime/bootstrap/builtin_capabilities.py`

To remove a capability safely, remove or disable it from the registry and then
remove/hide frontend UI that selects it.

### 3.4 Tools

Locations:

- `smarttutor/core/tool_protocol.py`
- `smarttutor/runtime/registry/tool_registry.py`
- `smarttutor/tools`
- `smarttutor/tools/builtin/__init__.py`

Tools are smaller single-purpose functions the agent can call during a turn.

Examples:

- `brainstorm`
- `web_search`
- `paper_search`
- `reason`
- `rag`
- `read_source`
- `read_memory`
- `write_memory`
- `read_skill`
- `exec`
- `code_execution`
- `list_notebook`
- `write_note`
- `web_fetch`
- `github`
- `cron`
- `ask_user`

Capabilities may expose different tool sets. The chat capability can mount
tools depending on context, such as whether a knowledge base or attachment is
present.

### 3.5 StreamBus And Stream Events

Locations:

- `smarttutor/core/stream.py`
- `smarttutor/core/stream_bus.py`

The backend streams structured events instead of returning only one final
string. This allows the UI and CLI to show:

- Stage changes.
- Thinking/progress messages.
- Tool calls.
- Tool results.
- Sources/citations.
- Final answer.
- Errors.
- User input pauses.

Keep this if you want real-time streaming UI.

### 3.6 Runtime Registries

Locations:

- `smarttutor/runtime/registry/tool_registry.py`
- `smarttutor/runtime/registry/capability_registry.py`
- `smarttutor/runtime/registry/deferred_tools.py`
- `smarttutor/runtime/registry/scoped_registry.py`

The registries decide which tools and capabilities exist at runtime.

For a custom project, this is where you control the available AI features.

## 4. Backend Structure

### 4.1 API Server

Location:

- `smarttutor/api/main.py`

Technology:

- FastAPI
- Uvicorn
- WebSockets
- CORS middleware

This file creates the backend app, configures lifecycle startup/shutdown, and
includes routers.

Startup does things such as:

- Ensure settings files exist.
- Export runtime settings to environment variables.
- Validate tool/capability consistency.
- Initialize LLM client.
- Start event bus.
- Auto-start partners.
- Start cron service.
- Check PocketBase if configured.
- Migrate old memory files if needed.

### 4.2 API Routers

Location:

- `smarttutor/api/routers`

Important routers include:

- `unified_ws.py`: main WebSocket endpoint for streaming turns.
- `chat.py`: chat-related HTTP API.
- `knowledge.py`: knowledge base management.
- `memory.py`: memory APIs.
- `settings.py`: runtime settings APIs.
- `tools.py`: tool settings.
- `skills.py`: skill management.
- `sessions.py`: session history.
- `attachments.py`: file upload and attachments.
- `partners.py`: partner/IM agent management.
- `book.py`: book engine APIs.
- `reading.py`: immersive reading APIs.
- `subagents.py`: connected coding agents/subagents.

For a smaller custom product, many routers can be hidden or removed, but do it
after checking frontend pages and imports.

### 4.3 WebSocket Endpoint

Location:

- `smarttutor/api/routers/unified_ws.py`

Main endpoint:

- `/api/v1/ws`

Supported message types include:

- `message` / `start_turn`
- `subscribe_turn`
- `subscribe_session`
- `resume_from`
- `unsubscribe`
- `cancel_turn`
- `submit_user_reply`
- `regenerate`
- `check_active_turn`
- `user_input`

This is what powers live chat in the web app.

## 5. Frontend Structure

Location:

- `web`

Technology:

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Framer Motion
- Chart.js
- Mermaid
- PDF.js
- docx-preview
- exceljs
- lucide-react icons

Important frontend folders:

- `web/app`: Next.js app routes.
- `web/components`: reusable UI components.
- `web/context`: React contexts.
- `web/lib`: frontend utilities and API clients.
- `web/locales`: i18n text for English and Chinese.
- `web/public`: logos, icons, images.
- `web/tests`: frontend/unit tests.

Important pages:

- `web/app/(workspace)/home/[[...sessionId]]/page.tsx`: main chat workspace.
- `web/app/(workspace)/book/page.tsx`: book feature.
- `web/app/(workspace)/co-writer/page.tsx`: co-writer feature.
- `web/app/(workspace)/partners/page.tsx`: partners UI.
- `web/app/(utility)/knowledge/page.tsx`: knowledge center.
- `web/app/(utility)/memory/page.tsx`: memory UI.
- `web/app/(utility)/settings/page.tsx`: settings.
- `web/app/(auth)/login/page.tsx`: login.
- `web/app/(admin)/admin/users/page.tsx`: admin users.

The frontend talks to the backend mostly through:

- HTTP API routes.
- WebSocket client code in `web/lib/unified-ws.ts`.

## 6. CLI Structure

Location:

- `smarttutor_cli`

Technology:

- Typer
- Rich
- prompt_toolkit

Main file:

- `smarttutor_cli/main.py`

CLI commands include:

- `smarttutor run`
- `smarttutor chat`
- `smarttutor kb`
- `smarttutor memory`
- `smarttutor partner`
- `smarttutor skill`
- `smarttutor plugin`
- `smarttutor session`
- `smarttutor notebook`
- `smarttutor provider`
- `smarttutor book`
- `smarttutor start`
- `smarttutor serve`

For a custom product, you can keep the CLI for developer/admin use or remove it
from distribution.

## 7. SDK / App Facade

Location:

- `smarttutor/app`
- `smarttutor/app/facade.py`

This provides `SmartTutorApp`, which wraps runtime operations such as:

- Starting a turn.
- Streaming a turn.
- Cancelling a turn.
- Submitting user replies.
- Regenerating the last turn.
- Listing sessions.
- Reading sessions.
- Renaming/deleting sessions.

The CLI uses this facade. It is useful to keep if you want Python-level access
without going through HTTP.

## 8. Knowledge Base And RAG

Locations:

- `smarttutor/knowledge`
- `smarttutor/services/rag`
- `smarttutor/tools/rag_tool.py`
- `smarttutor/tools/builtin/__init__.py`

Supported RAG/document engines include:

- LlamaIndex
- PageIndex
- GraphRAG
- LightRAG
- LightRAG Server
- Tencent IMA
- MarginNote 4
- Linked Obsidian vaults

Document parsing engines include:

- PyMuPDF
- pdfplumber
- pypdf
- python-docx
- openpyxl
- python-pptx
- Apache Tika
- Docling
- MarkItDown
- PyMuPDF4LLM
- LiteParse
- MinerU integration/config

This system lets the user create knowledge bases from documents and then ask
questions grounded in those documents.

If your new project needs custom files, manuals, textbooks, policies, company
docs, course material, or legal/medical documents, keep this subsystem.

If your project is only a simple chatbot, this subsystem can be removed or
hidden, but it touches many UI and tool areas.

## 9. Memory System

Locations:

- `smarttutor/services/memory`
- `smarttutor/learning`
- `web/app/(utility)/memory`

The memory system stores information across sessions. It has multiple layers:

- L1 traces: raw evidence/events.
- L2 surface summaries: organized summaries for different surfaces.
- L3 synthesis: higher-level long-term memory.

The UI provides memory pages and a graph.

For a custom project:

- Keep it if personalization matters.
- Remove or hide it if privacy/simplicity is more important.
- If kept, clearly document what memory is stored and give users control.

## 10. Learning And Mastery

Locations:

- `smarttutor/learning`
- `smarttutor/capabilities/mastery`
- `web/app/(utility)/space/learning`

This subsystem supports guided learning paths, grading, mastery policy, pending
questions, and scheduled practice.

Keep this if the new project is educational.
Remove or hide it if the new project is not about learning.

## 11. Question Bank

Locations:

- `smarttutor/tools/question_bank.py`
- `smarttutor/tools/question`
- `web/app/(utility)/space/questions`

The question bank stores and manages generated or imported questions. It is
used by mastery practice and quiz workflows.

Keep this for education, exam prep, or training products.

## 12. Book Engine

Locations:

- `smarttutor/book`
- `web/app/(workspace)/book`
- `smarttutor/api/routers/book.py`

The book engine can compile interactive/living book pages from learning
material. It has prompts for blocks such as:

- Text
- Timeline
- Section
- Page plan
- Interactive block
- Flash cards
- Figures
- Deep dive
- Code
- Callouts
- Animation

Keep this if the new product creates course modules, study books, tutorials, or
documentation.

Remove or hide it for a simpler assistant.

## 13. Co-Writer

Locations:

- `smarttutor/co_writer`
- `web/app/(workspace)/co-writer`
- `smarttutor/api/routers/co_writer.py`

This is a writing assistant area with document editing and prompts.

Keep it if your product includes essay writing, content drafting, reports, or
student writing help.

## 14. Visualization And Math Animation

Locations:

- `smarttutor/agents/visualize`
- `smarttutor/agents/math_animator`
- `smarttutor/tools/vision`

Technologies:

- SVG
- HTML
- Chart.js
- Mermaid
- Manim for rendered math animations

Capabilities:

- `visualize`
- `math_animator`

Keep this if visual explanations are important.

Remove or hide if you only need text chat.

## 15. Partners And External Agent Channels

Locations:

- `smarttutor/partners`
- `smarttutor/services/partners`
- `web/app/(workspace)/partners`
- `smarttutor_cli/partner.py`

Partner channels include integrations for services such as:

- Telegram
- Slack
- Discord
- Matrix
- Teams-like channels
- Mattermost
- Feishu
- DingTalk
- WeCom
- WhatsApp
- Email
- Zulip

This is a large subsystem for IM-connected companions.

For most custom projects, this is a good candidate to remove or hide at first.
It adds complexity, credentials, channel SDKs, background services, and runtime
concerns.

## 16. MCP, Plugins, Skills, And CLI Apps

Locations:

- `smarttutor/services/mcp`
- `smarttutor/plugins`
- `smarttutor/skills`
- `smarttutor_cli/plugin.py`
- `smarttutor_cli/skill.py`
- `web/app/(utility)/settings/mcp`
- `web/app/(utility)/space/skills`
- `web/app/(utility)/space/mcp`
- `web/app/(utility)/space/cli-apps`

These systems let the assistant connect to external tools and user-authored
skills.

Keep if you want an extensible agent platform.
Hide/remove if you want a controlled product with fewer moving parts.

## 17. Authentication And Multi-User Support

Locations:

- `smarttutor/api/routers/auth.py`
- `smarttutor/multi_user`
- `web/app/(auth)`
- `web/app/(admin)`
- `smarttutor/services/pocketbase_client.py`

Technology:

- JWT
- bcrypt
- PocketBase integration

The app supports local single-user mode and optional auth/multi-user behavior.

For a new product:

- Keep auth if you deploy for multiple users.
- Simplify auth if this is only local/personal.
- Remove admin UI if not needed.

## 18. Settings And Configuration

Locations:

- `smarttutor/services/config`
- `smarttutor/config`
- `web/app/(utility)/settings`
- `.env.example`

Important point:

- Runtime settings live in `data/user/settings/*.json`.
- Project-root `.env` files are intentionally not the primary runtime config.

Settings include:

- LLM providers.
- Embeddings.
- Search.
- Memory.
- Tools.
- Capabilities.
- Document parsing.
- Attachments.
- Image/video/STT/TTS.
- Network/CORS.

For a custom project, settings are one of the safest places to customize
defaults without changing core code.

## 19. LLM Providers And AI Services

Locations:

- `smarttutor/services/llm`
- `smarttutor/services/provider_registry.py`
- `smarttutor/services/model_selection`
- `web/public/provider-icons`
- `web/app/(utility)/settings/llm`
- `web/app/(utility)/settings/models`

The project supports many OpenAI-compatible providers and specific SDKs. Based
on dependencies and UI assets, it includes support or configuration for:

- OpenAI
- Anthropic
- Gemini
- DeepSeek
- OpenRouter
- Ollama
- LM Studio
- NVIDIA
- Qwen / DashScope
- Perplexity
- Groq
- Mistral
- Cohere
- Azure
- Baidu
- ByteDance / Doubao
- Zhipu
- SiliconCloud
- and others

For a new project, choose fewer providers at first. Supporting every provider
adds UI, testing, and configuration complexity.

## 20. Storage

Common runtime storage is under:

- `data/user`

This folder may contain:

- Settings.
- Sessions.
- Knowledge base indexes.
- Memory.
- Runtime state.
- User files.

Do not casually delete `data/user` in a real installation.

## 21. Packaging And Deployment

Important files:

- `pyproject.toml`
- `requirements.txt`
- `requirements/*.txt`
- `Dockerfile`
- `Dockerfile.runner`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.ghcr.yml`
- `compose.yaml`
- `CONTAINERIZATION.md`

Python package:

- Name: `smarttutor`
- Python: `>=3.11,<3.14`
- CLI script: `smarttutor = smarttutor_cli.main:main`

Frontend package:

- `web/package.json`
- App name: `opentutor-web`
- Next.js 16
- React 19

Deployment options:

- Local Python install.
- `smarttutor start`.
- API-only server with `smarttutor serve`.
- Docker Compose.
- GHCR images.

## 22. Tests

Backend tests:

- `tests`
- Some package-level tests under `smarttutor/learning/tests`

Frontend tests:

- `web/tests`

Frontend scripts:

- `npm run test:node`
- `npm run lint`
- `npm run build`
- `npm run i18n:check`

Python dev tools:

- pytest
- ruff
- black
- pre-commit
- bandit
- safety

When removing modules, tests will reveal missing imports and broken surfaces.

## 23. What To Keep For A New Project

For most custom AI products, keep these:

- `smarttutor/core`
- `smarttutor/runtime`
- `smarttutor/app`
- `smarttutor/api/main.py`
- `smarttutor/api/routers/unified_ws.py`
- `smarttutor/agents/chat`
- `smarttutor/services/llm`
- `smarttutor/services/config`
- `smarttutor/services/session`
- `web/app/(workspace)/home`
- `web/components/chat`
- `web/lib/unified-ws.ts`

Keep these if the product needs documents/RAG:

- `smarttutor/knowledge`
- `smarttutor/services/rag`
- `smarttutor/services/parsing`
- `smarttutor/tools/rag_tool.py`
- `web/app/(utility)/knowledge`
- attachment APIs and UI

Keep these if the product is education-focused:

- `smarttutor/learning`
- `smarttutor/capabilities/mastery`
- `smarttutor/tools/question_bank.py`
- `smarttutor/tools/question`
- question UI pages

Keep these if personalization matters:

- `smarttutor/services/memory`
- memory tools
- memory UI pages

## 24. Good Candidates To Remove Or Hide First

If the goal is a simpler custom project, hide before deleting:

- Partners / IM channels.
- Book engine.
- Co-writer.
- Math animator.
- Advanced visualization.
- MCP settings.
- External CLI apps.
- Plugin marketplace.
- Admin user management.
- Excess provider settings.
- Voice/video/image generation if not needed.

Hiding routes and navigation is safer than deleting code immediately.

## 25. Safe Customization Strategy

Use this order to avoid breaking the program:

1. Rebrand UI text, logo, app name, and colors.
2. Hide unwanted frontend navigation items.
3. Disable unwanted capabilities in settings or registry.
4. Disable unwanted tools in tool settings.
5. Run backend and frontend tests.
6. Remove backend routers only after the UI no longer calls them.
7. Remove Python dependencies only after imports are gone.
8. Remove frontend dependencies only after components/pages are gone.
9. Rename Python package only if needed, and do it last.

Do not start by renaming every `smarttutor` import. That is risky because the
Python package name is used throughout the backend, CLI, tests, docs, and
packaging.

## 26. How To Disable A Capability Safely

Example target:

- remove `math_animator`

Steps:

1. Hide the frontend button/dropdown option that selects `math_animator`.
2. Remove or disable `math_animator` from
   `smarttutor/runtime/bootstrap/builtin_capabilities.py`.
3. Check capability settings pages for references.
4. Remove Manim-specific settings only after no UI uses them.
5. Run tests.
6. Remove dependencies from `pyproject.toml` only after imports are gone.

The same strategy applies to:

- `visualize`
- `deep_research`
- `deep_question`
- `mastery_path`
- `immersive_reading`

## 27. How To Disable A Tool Safely

Example target:

- remove `web_search`

Steps:

1. Hide it from `/settings/tools` UI.
2. Remove it from built-in tool registration.
3. Remove it from any capability manifest that references it.
4. Keep tests updated.
5. Confirm `smarttutor/api/main.py` startup validation does not report config
   drift.

Important:

- The backend validates that capabilities do not reference missing tools.
- If a capability references a tool that is not registered, startup can fail.

## 28. How To Rebrand Safely

Common places to update:

- `README.md`
- `pyproject.toml`
- `web/package.json`
- `web/public/logo.png`
- `web/public/logo_black.png`
- `web/public/favicon-*`
- `web/locales/en/*.json`
- `web/locales/zh/*.json`
- `smarttutor/runtime/banner.py`
- frontend layout/navigation components

Recommended approach:

- First change visual branding and user-facing copy.
- Keep internal package names as `smarttutor` until the product works.
- Rename the Python package only in a later cleanup phase.

## 29. How To Make It Our Own Product

A practical path:

### Phase 1: Product Definition

Decide:

- Product name.
- Target users.
- Main use case.
- Which features are core.
- Which features should be hidden.
- Which LLM providers to support.
- Whether it is local-only or multi-user.

### Phase 2: UI Simplification

Start with:

- Main chat page.
- Knowledge page if documents matter.
- Settings page with only required provider fields.

Hide:

- Partners.
- Book.
- Co-writer.
- Memory graph if not needed.
- Admin if not needed.
- Extra provider pages.

### Phase 3: Capability Simplification

Keep:

- `chat`

Optional:

- `deep_solve` for problem solving.
- `deep_research` for research.
- `visualize` for diagrams.
- `mastery_path` for education.

Disable everything else until needed.

### Phase 4: Backend Cleanup

After the UI is stable:

- Remove unused routers.
- Remove unused services.
- Remove unused dependencies.
- Update tests.
- Update Docker and packaging.

### Phase 5: Rename Package

Only after the application works:

- Rename CLI command.
- Rename package metadata.
- Rename Python import package if truly necessary.
- Update Docker images and docs.

## 30. Dependency Map By Feature

### Core Chat

Uses:

- `smarttutor/core`
- `smarttutor/runtime`
- `smarttutor/agents/chat`
- `smarttutor/services/llm`
- `smarttutor/services/session`
- `smarttutor/api/routers/unified_ws.py`
- `web/app/(workspace)/home`
- `web/components/chat`
- `web/lib/unified-ws.ts`

Can remove:

- RAG, memory, partners, book, co-writer, advanced tools, if not referenced.

### Document Chat / RAG

Uses:

- `smarttutor/knowledge`
- `smarttutor/services/rag`
- `smarttutor/services/parsing`
- `smarttutor/tools/rag_tool.py`
- `smarttutor/api/routers/knowledge.py`
- `web/app/(utility)/knowledge`
- attachment handling

Dependencies:

- LlamaIndex
- FAISS
- PyMuPDF
- pypdf
- pdfplumber
- python-docx
- openpyxl
- python-pptx

### Research

Uses:

- `smarttutor/agents/research`
- `smarttutor/tools/web_search.py`
- `smarttutor/tools/paper_search_tool.py`
- search provider settings

Dependencies:

- ddgs
- arxiv
- provider-specific search APIs if configured

### Visualization

Uses:

- `smarttutor/agents/visualize`
- frontend rendering of HTML/SVG/Chart/Mermaid outputs

Dependencies:

- Chart.js
- Mermaid
- React markdown/rendering libraries

### Math Animation

Uses:

- `smarttutor/agents/math_animator`

Dependencies:

- Manim
- ffmpeg
- LaTeX/system packages depending on render type

### Memory

Uses:

- `smarttutor/services/memory`
- memory tools
- memory UI pages

Depends on:

- local file storage
- LLM calls for consolidation

### Partners

Uses:

- `smarttutor/partners`
- `smarttutor/services/partners`
- partner channel SDKs

Dependencies:

- Slack SDK
- Telegram SDK
- Matrix SDK
- Discord HTTP/WebSocket logic
- multiple IM platform libraries

This is high complexity. Remove/hide early if not needed.

## 31. Warning Areas

Be careful changing these:

- `smarttutor/runtime/orchestrator.py`: central turn execution.
- `smarttutor/core/stream.py`: event contract used by frontend and CLI.
- `smarttutor/core/context.py`: request contract.
- `smarttutor/runtime/registry/*`: tool/capability loading.
- `smarttutor/services/config/*`: settings are used across many modules.
- `web/lib/unified-ws.ts`: frontend streaming contract.
- `smarttutor/api/routers/unified_ws.py`: backend streaming contract.
- `pyproject.toml`: dependency and package metadata.

Breaking these can affect the whole app.

## 32. Recommended Minimal Custom Version

If we want a clean first version of our own project, keep:

- Chat UI.
- LLM settings.
- Session history.
- File attachments.
- Knowledge base/RAG if our product needs documents.
- One or two custom capabilities.

Hide:

- Partners.
- Book.
- Co-writer.
- Admin.
- MCP.
- Skills marketplace.
- Math animator.
- Voice/video/image generation.
- Extra provider pages.

This gives a simpler product while preserving the powerful runtime.

## 33. Suggested Next Files To Inspect Before Editing

For UI changes:

- `web/app/(workspace)/layout.tsx`
- `web/app/(workspace)/home/[[...sessionId]]/page.tsx`
- `web/components/chat`
- `web/components/app shell/navigation files`
- `web/locales/en/app.json`
- `web/locales/en/common.json`

For backend feature changes:

- `smarttutor/runtime/bootstrap/builtin_capabilities.py`
- `smarttutor/tools/builtin/__init__.py`
- `smarttutor/api/main.py`
- `smarttutor/api/routers`
- `smarttutor/runtime/registry`

For packaging/rebrand:

- `pyproject.toml`
- `web/package.json`
- `Dockerfile`
- `docker-compose.yml`
- `README.md`

## 34. Final Summary

SmartTutor is best treated as a modular AI agent platform with an education
product built on top. The safest way to create our own project is to keep the
runtime, chat, LLM, session, streaming, and optional RAG modules, then hide or
remove advanced surfaces one by one.

Do not delete large folders at the start. First hide UI routes and disable
capabilities/tools. Then run tests. Once the app is stable, remove unused code
and dependencies.
