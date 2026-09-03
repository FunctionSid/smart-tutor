# Smart Tutor

Smart Tutor is an agent-native learning workspace for tutoring, document study,
guided practice, quizzes, revision, and RAG-backed reading. It exposes the same
runtime through a local web app, CLI, WebSocket API, and Python SDK.

## What It Does

- Tutor from uploaded documents, knowledge bases, Reader materials, and prior sessions.
- Turn Library content into explanations, summaries, quizzes, tests, practice, and revision.
- Keep learner progress, mastery state, question history, memory, and sessions connected.
- Support OpenAI-compatible, OpenAI, Anthropic, Ollama/local, and other configured providers.
- Preserve advanced RAG engines, document parsing, WebSocket streaming, voice/STT/TTS, and accessibility surfaces.

## Quick Start

Use Python 3.11-3.13 and Node.js 20+.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .

cd web
npm ci --legacy-peer-deps
cd ..

smarttutor init
smarttutor start --dev
```

The default backend runs on `http://127.0.0.1:8001`; the frontend runs on the
port printed by `smarttutor start`.

## CLI

```bash
smarttutor run chat "Explain Fourier transform"
smarttutor run deep_solve "Solve x^2 = 4"
smarttutor run visualize "Show how derivatives work"
smarttutor kb list
smarttutor memory show
```

Provider auth (`openai-codex` OAuth login; `github-copilot` validates an existing Copilot auth session; `codebuddy` validates CodeBuddy SDK auth and starts login when needed)

## Container Notes

Container deployments that need browser-based Codex OAuth can use the temporary
local bridge documented in [CONTAINERIZATION.md#temporary-local-codex-oauth-bridge](CONTAINERIZATION.md#temporary-local-codex-oauth-bridge).

## Core Packages

- `smarttutor/`: backend runtime, APIs, capabilities, tools, RAG, memory, providers, and services.
- `smarttutor_cli/`: Typer CLI entry point.
- `smarttutor_web/`: packaged frontend assets for the full distribution.
- `web/`: Next.js frontend source.
- `tests/`: Python test suite.
- `web/tests/`: frontend unit tests.

## Development Checks

```bash
python -m compileall smarttutor smarttutor_cli
python -m pytest

cd web
npm test
npm run build
```

## Optional Provider Addons

Most provider adapters use HTTP-compatible APIs or optional SDKs. The DashScope
embedding adapter imports the `dashscope` SDK lazily; install it only when using
Aliyun/DashScope native embeddings:

```bash
python -m pip install "smarttutor[dashscope]"
```

## License

Apache-2.0. See [LICENSE](LICENSE).
