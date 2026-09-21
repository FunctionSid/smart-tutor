# Smart Tutor Optimization Recommendations

Last updated: 2026-09-11 IST

This is an investigation note, not an implementation log. It records recommended
stability and performance improvements while keeping Smart Tutor's current
features and behavior intact.

## Current Baseline

Smart Tutor already has several important stability foundations:

- Main chat, RAG, model selection, voice STT/TTS, Hands-Free, Exam Mode, memory,
  and MCP surfaces are covered by focused tests.
- LlamaIndex RAG can use FAISS for new or re-indexed knowledge bases, with
  legacy SimpleVectorStore indexes still readable.
- RAG retrieval has an in-process loaded-index cache keyed by storage freshness.
- LLM providers are pooled per event loop to preserve HTTP keep-alive.
- WebSocket turns can reconnect, replay persisted events, cancel running turns,
  and mark stale running turns after a server restart.
- Production source launches avoid long-running `next dev` by building and
  reusing a standalone Next.js output.
- Recent Krutrim Cloud and Jarvis keyboard-toggle work is verified by focused
  Python and Node tests.
- Provider model discovery is cached for a short TTL, keyed per provider/base
  URL/non-secret credential fingerprint, with stale cached results kept during
  provider failure backoff and manual sync preserved as a forced refresh.
- The Windows BAT startup path now waits for backend/frontend readiness before
  opening the browser and has been verified at `http://localhost:3782`.
- A repeatable health-smoke script now checks frontend, backend, system status,
  system diagnostics, knowledge, exam, LLM options, and wake probe endpoints.
- Read-only system diagnostics expose provider-pool and LlamaIndex index-cache
  status for troubleshooting.
- Hands-Free backend wake/STT/TTS endpoints are verified live; real microphone
  speech remains the main unverified part.
- A Microsoft Edge frontend link/keyboard crawl visited 39 internal routes on
  2026-09-10; primary navigation is reachable, and Settings tab keyboard
  navigation works.
- Memory update/audit/dedup runs now surface selected-model and no-op/error
  outcomes instead of silently falling back or looking idle.

## What Appears Broken Or Not Fully Verified

These are not all confirmed runtime bugs. They are the current weak spots found
from the code and documentation pass:

| Area | Current Status | Risk |
| :--- | :--- | :--- |
| Global system Python pytest | Known broken | Docs record `ModuleNotFoundError: No module named '_pytest.cacheprovider'`; use `.\.venv\Scripts\python.exe -m pytest` until the system Python environment is repaired. |
| Full frontend lint on Windows | Improved | `npm run lint` now completes through the Windows-safe wrapper with 0 errors. It still reports 129 existing warnings, so warning cleanup remains open. |
| Krutrim per-model behavior | Not fully verified | Discovery and `gpt-oss-20b` chat/tool-call paths work, but every discovered Krutrim model has not been tested for streaming, tool calling, and RAG behavior. |
| Hands-Free live microphone path | Partially verified | State-machine, shortcut wiring, wake probe, STT facade, and TTS pieces are tested. Live backend wake/STT/TTS endpoints pass, but live spoken "Hey Jarvis" and real browser microphone automation remain open. |
| Frontend accessibility polish | Improved | The 2026-09-10 H1 and accessible-name gaps were fixed and verified in Microsoft Edge. Broader manual screen-reader verification remains open. |
| Playwright default browser cache | Tooling gap | `npm run audit` fails before app testing because the default Playwright Chromium executable is missing locally. Microsoft Edge based Playwright checks work. |
| NVDA/screen-reader verification | Not fully verified | Automated accessibility tests cover key regions, but manual NVDA verification was not performed after the latest Hands-Free shortcut update. |
| Large frontend/backend modules | Maintainability risk | Several files exceed 1,000 lines, including `smarttutor/api/routers/knowledge.py`, `smarttutor/services/session/turn_runtime.py`, `web/components/chat/home/TracePanels.tsx`, `web/context/UnifiedChatContext.tsx`, and `web/components/chat/home/ChatMessages.tsx`. Large files make regressions harder to isolate. |
| Empty L2/L3 memory docs | Product-data gap | The Memory pipeline is wired, and the `quiz` L1 surface now includes LearningStore and exam-attempt evidence. Useful durable personalization still requires an intentional Memory Run over real data; Smart Tutor does not auto-build user memory docs yet. |

## Top 3 Recommendations

### 1. Make model discovery cached, per-provider, and non-blocking

Status: completed and verified on 2026-09-09.

Why it matters:

- The chat page currently refreshes LLM options with `refreshLocal: true` on
  initial load.
- That refresh now includes both Ollama discovery and Krutrim Cloud discovery.
- Local providers can be offline, and cloud provider discovery can be slow,
  rate-limited, or temporarily unavailable.

Recommended change:

- Add a short TTL cache for provider model discovery results, keyed by provider,
  base URL, and non-secret credential fingerprint.
- Refresh models in the background while showing the last known catalog.
- Add per-provider failure backoff so an offline Ollama server or a failing cloud
  `/v1/models` endpoint is not retried on every page focus/load.
- Keep a manual "Sync models" action that bypasses the TTL.

Expected benefit:

- Faster chat startup.
- Fewer startup stalls when a provider is offline.
- Less unnecessary network traffic and fewer provider-rate surprises.
- Keeps Ollama, Krutrim, OpenAI, and future providers working exactly as they do
  now, only with smarter refresh timing.

Verified:

- Unit tests cover TTL hits, expired refresh, forced refresh, provider failure
  backoff, stale results during offline provider failures, and secret-safe cache
  keys.
- Frontend node tests cover background model refresh preserving the current
  catalog and manual sync sending `force_refresh=true`.
- Live provider matrix smoke remains deferred to the repeatable health-smoke
  suite in recommendation 2.

### 2. Add a repeatable health-smoke suite for the real user flows

Status: implemented for endpoint-level health on 2026-09-10. Provider-heavy,
real microphone, and full browser speech checks remain future extensions.

Why it matters:

- Many pieces are tested in isolation, but the highest-risk paths cross several
  layers: browser, WebSocket, selected model, RAG context, STT/TTS, and persisted
  session state.
- Current docs still list manual verification gaps for Hands-Free, Krutrim
  per-model behavior, and NVDA.

Recommended change:

- Create a single command such as `scripts/smoke_smart_tutor.ps1` or
  `python -m scripts.smoke_smart_tutor` that runs a small matrix:
  - Backend health and settings load.
  - LLM options load from cached catalog.
  - One selected Ollama chat completion if Ollama is available.
  - One selected Krutrim chat completion if env key is available.
  - One Krutrim tool-call probe for at least the preferred model.
  - One RAG query against a tiny fixture KB.
  - Voice STT facade probe with generated audio.
  - Hands-Free route/probe checks.
- Keep provider-dependent checks skippable with clear "skipped because not
  configured" output rather than hard failing.

Expected benefit:

- Faster confidence before editing large surfaces.
- Clearer distinction between "broken", "not configured", and "not verified".
- Catches the real failures users feel, not only isolated unit-level regressions.

Suggested verification:

- Run the smoke suite locally and record a concise PASS/SKIP/FAIL summary.
- Add CI-safe mode that skips live providers and microphone-only checks.
- Add optional local mode for browser microphone automation when a fake device is
  configured.

Verified:

- `scripts/smoke_smart_tutor.py` returned `9 passed, 0 skipped, 0 failed`
  against the live local app.

### 3. Make RAG/provider resource limits configurable and visible

Status: partially implemented on 2026-09-10. Read-only diagnostics exist for the
provider pool and LlamaIndex index cache. Tunable limits, hit/miss counters,
vector-store backend reporting, and process-memory reporting are still open.

Why it matters:

- The LLM provider pool is intentionally small (`_PROVIDER_POOL_MAXSIZE = 2`).
- The loaded LlamaIndex cache is also intentionally small
  (`_INDEX_CACHE_MAXSIZE = 2`, idle expiry 10 minutes).
- Those defaults are reasonable for a small single-user desktop setup, but the
  best value depends on RAM, KB size, provider count, and how often the user
  switches between models/knowledge bases.

Recommended change:

- Expose read-only diagnostics for:
  - active provider-pool size,
  - active RAG index-cache entries,
  - cache hit/miss/prune counters,
  - detected vector-store backend per KB (`faiss` vs `simple`),
  - approximate process memory used by backend/frontend children.
- Add bounded settings for:
  - provider pool size,
  - RAG index cache size,
  - RAG index idle expiry,
  - optional "prefer FAISS re-index" guidance for legacy SimpleVectorStore KBs.
- Keep defaults conservative, but let power users tune for their machine.

Expected benefit:

- Fewer reloads/rebuilds when switching between two or more KBs or cloud/local
  providers.
- Better memory control on smaller machines.
- Easier diagnosis when Smart Tutor feels slow after model or KB switching.

Suggested verification:

- Unit tests for cache configuration clamps and diagnostics payloads.
- Retrieval timing comparison for cold vs warm KB searches.
- Memory snapshot before and after repeated model/KB switching.

## Additional Recommendations

### Split the largest modules by responsibility

Large files are not automatically broken, but they slow review and increase
regression risk. Good candidates:

- `smarttutor/api/routers/knowledge.py`: split route handlers, upload/indexing
  helpers, and response shaping.
- `smarttutor/services/session/turn_runtime.py`: split request normalization,
  event persistence, title generation, and execution lifecycle helpers.
- `web/context/UnifiedChatContext.tsx`: split socket lifecycle, message state,
  persistence/reconciliation, and user actions into hooks.
- `web/components/chat/home/TracePanels.tsx`: split provider trace rows,
  tool-call panels, event grouping, and filtering.
- `web/components/chat/home/ChatMessages.tsx`: split message rendering,
  generated artifacts, thinking blocks, and accessibility status handling.

Preserve behavior by moving code behind existing tests first, then add narrower
tests for the extracted units.

### Finish frontend warning cleanup on Windows

The full lint command now runs successfully on Windows. The remaining work is to
reduce or intentionally document the existing warning set so new warnings are
easier to spot.

Recommended next step:

- Group current warnings by rule.
- Fix low-risk warnings first, especially simple i18n/no-literal-text cases in
  touched UI areas.
- Decide whether any warnings should become explicit project exceptions rather
  than recurring noise.

### Reduce accidental global runtime resets

Applying catalog settings resets global LLM and embedding clients. That is
documented in code as affecting in-flight turns. The behavior is understandable,
but it is a stability footgun during active sessions.

Recommended next step:

- Prefer generation-scoped provider/client selection for new turns.
- When settings change, retire old clients after in-flight calls complete where
  possible.
- Surface a UI warning if a catalog apply occurs while turns are running.

### Add provider capability probes

For OpenAI-compatible providers, model discovery only says the model exists; it
does not prove streaming, JSON/tool calling, vision, reasoning settings, or
`response_format` support.

Recommended next step:

- Store lightweight capability probe results per `(provider, model)`.
- Probe only on demand or in background after model sync.
- Use probe results to label models in the selector, for example "tool calling
  verified", "chat only", or "streaming unverified".

### Add a Hands-Free live test mode

Hands-Free currently has good unit coverage but still needs a practical live
confidence path.

Recommended next step:

- Add a dev-only page or Playwright fixture mode that can feed deterministic
  audio into the microphone path.
- Verify `Ctrl+H`, `Ctrl+R`, wake detection, STT submission, cancel/barge-in,
  and TTS playback state transitions in one browser script.

### Continue frontend accessibility verification

The 2026-09-10 link/keyboard crawl found small, concrete gaps rather than broad
navigation breakage. The H1 and accessible-name gaps from that crawl have been
fixed. Remaining work is verification depth, not the original labels/headings.

Recommended next step:

- Point `npm run audit` at the installed Edge channel or refresh the Playwright
  Chromium cache so the built-in audit can run repeatably.
- Run manual NVDA/Edge checks through chat, Settings, Exam, Knowledge, Memory,
  and Hands-Free controls.

## Suggested Next Implementation Order

1. Model discovery TTL/background refresh. Completed 2026-09-09.
2. Health-smoke suite with PASS/SKIP/FAIL output. Endpoint-level version completed 2026-09-10.
3. Cache diagnostics. Read-only provider/RAG diagnostics partially completed 2026-09-10.
4. Make the built-in Playwright audit repeatable again, or point it at Edge.
5. Add a Hands-Free live browser microphone/speaker verification mode.
6. Provider capability probes for Krutrim and other OpenAI-compatible providers.
7. Clean up or document the existing frontend lint warnings.
8. Add tunable RAG/provider cache limits if diagnostics show real pressure.
9. Split the largest modules behind existing tests.

This order improves stability first, then performance visibility, then long-term
maintainability.
