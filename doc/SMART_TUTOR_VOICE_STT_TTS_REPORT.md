# Smart Tutor Voice, STT, and TTS Technical Report

Source project: SmartTutor v1.5.16  
Target product: Smart Tutor  
Report scope: voice, speech-to-text, text-to-speech, audio capture, audio playback, settings, dependencies, and future migration plan.

This report is based on the current source tree. It does not require code changes, package installation, deployment, or config edits.

## 1. Executive Summary

SmartTutor already has a usable voice layer, but it is mostly a provider adapter layer rather than a full local voice system.

Current capabilities:

- Browser microphone dictation in the chat composer.
- Backend STT endpoint at `/api/v1/voice/stt`.
- Assistant reply read-aloud button using TTS.
- Backend TTS endpoint at `/api/v1/voice/tts`.
- Settings pages for TTS and STT provider/model selection.
- OpenAI-compatible HTTP adapters for OpenAI, OpenRouter, Groq, SiliconFlow, Azure OpenAI, custom OpenAI-compatible services, and local OpenAI-compatible servers.
- PCM-to-WAV wrapping for raw PCM TTS responses so browsers can play the output.
- Global and per-session voice autoplay support.

Current limitations:

- No built-in local Whisper, faster-whisper, whisper.cpp, Piper, Kokoro, or Windows native TTS adapter exists in the source.
- No real-time streaming STT is implemented in the chat voice path.
- No streaming TTS is exposed to the frontend; the backend returns one complete audio response.
- No voice activity detection, push-to-talk waveform, interruption, barge-in, pronunciation dictionary, captions, or transcript confidence UI is implemented.
- STT and TTS are configured as shared service profiles, not per-course/per-student learning preferences.

Best Smart Tutor direction:

- Keep the existing `/api/v1/voice/*` endpoints, settings catalog, frontend hooks, and adapter registry.
- Add local provider adapters behind the same interface.
- Keep cloud voice as the Railway-friendly default.
- Add local voice as an optional desktop/private deployment mode.
- Build the Smart Tutor voice experience in four phases, not many phases.

## 2. Current Voice Architecture

```text
Chat UI
  |-- microphone button -> useVoiceRecorder -> POST /api/v1/voice/stt
  |-- speaker button    -> ChatMessages VoiceButton -> POST /api/v1/voice/tts

FastAPI
  |-- smarttutor/api/main.py includes voice router at /api/v1/voice
  |-- smarttutor/api/routers/voice.py exposes /tts and /stt

Voice service facade
  |-- smarttutor/services/voice/__init__.py
      |-- synthesize_speech()
      |-- transcribe_audio()

Runtime config
  |-- smarttutor/services/config/provider_runtime.py
      |-- TTS_PROVIDERS
      |-- STT_PROVIDERS
      |-- resolve_tts_runtime_config()
      |-- resolve_stt_runtime_config()

Adapters
  |-- smarttutor/services/voice/adapters/__init__.py
      |-- get_tts_adapter()
      |-- get_stt_adapter()
  |-- smarttutor/services/voice/adapters/openai_compat.py
      |-- OpenAICompatTTSAdapter
      |-- OpenRouterTTSAdapter
      |-- OpenAICompatSTTAdapter
```

The voice design is already modular:

- API layer handles HTTP request/response details.
- Service layer resolves active provider settings and selects an adapter.
- Adapter layer talks to the provider.
- Frontend hooks know only the `/api/v1/voice/*` endpoints.

That means Smart Tutor can add local voice engines without changing the chat UI too much.

## 3. Backend Voice Files

### `smarttutor/api/main.py`

Purpose:

- Registers the voice router.
- Mounts it at `/api/v1/voice`.
- Applies the same API authentication dependency used by other protected API routers.

Current behavior:

- Voice endpoints are available through the main FastAPI app.
- Voice is treated as shared infrastructure, not a separate standalone service.

Keep/remove guidance:

- Keep.
- For Smart Tutor, keep this routing style and add new endpoints only if live streaming voice is introduced.

### `smarttutor/api/routers/voice.py`

Purpose:

- HTTP surface for TTS and STT.

Routes:

- `POST /api/v1/voice/tts`
- `POST /api/v1/voice/stt`

TTS request:

```json
{
  "text": "Assistant message text",
  "voice": "optional provider voice override",
  "format": "optional output format override"
}
```

TTS response:

- Raw audio bytes.
- Media type from provider, normalized where possible.
- `Cache-Control: no-store`.

Important TTS details:

- Calls `synthesize_speech()`.
- Converts raw PCM responses to WAV for browser compatibility.
- Recognizes PCM content types:
  - `audio/pcm`
  - `audio/x-pcm`
  - `audio/l16`
- Default PCM fallback:
  - sample rate: `24000`
  - channels: `1`
  - sample width: 16-bit PCM

STT request:

- Multipart upload field: `file`
- Optional form field: `language`

STT response:

```json
{
  "text": "transcribed text"
}
```

Important STT details:

- Reads the entire uploaded file into memory.
- Rejects empty uploads with HTTP 400.
- Rejects uploads larger than 25 MB with HTTP 413.
- Sends filename, content type, bytes, and optional language to `transcribe_audio()`.

Error mapping:

- `ValueError` -> HTTP 400
- `VoiceProviderError` -> HTTP 502

Keep/remove guidance:

- Keep.
- Good base for Smart Tutor.
- Modify later for streaming only if live conversation is required.
- Add duration checks and MIME allow-list in a future hardening phase.

### `smarttutor/services/voice/__init__.py`

Purpose:

- Public voice service facade used by the API router and settings diagnostics.

Functions:

- `synthesize_speech()`
- `transcribe_audio()`

TTS flow:

1. Resolve active TTS runtime config from the model catalog.
2. Apply optional per-call voice/format override.
3. Strip Markdown for speech by default.
4. Select adapter by config adapter name.
5. Return complete audio bytes and content type.

STT flow:

1. Resolve active STT runtime config from the model catalog.
2. Apply optional language override.
3. Select adapter by config adapter name.
4. Return transcribed text.

Keep/remove guidance:

- Keep.
- This is the best place to preserve a stable Smart Tutor voice API.
- Add local adapters below this layer, not by changing frontend calls first.

### `smarttutor/services/voice/base.py`

Purpose:

- Abstract base classes and helpers shared by all voice adapters.

Classes:

- `VoiceProviderError`
- `VoiceProviderHTTPError`
- `BaseTTSAdapter`
- `BaseSTTAdapter`

Helpers:

- `build_auth_headers()`
- `join_audio_path()`
- `strip_markdown_for_speech()`

Auth styles supported:

- `bearer`: `Authorization: Bearer <key>`
- `api_key_header`: `api-key: <key>`
- `token`: `Authorization: Token <key>`

Markdown stripping behavior:

- Removes fenced code blocks.
- Removes Markdown tables.
- Removes images.
- Converts links to visible text.
- Removes heading/list/blockquote markers.
- Removes HTML tags.
- Trims to `max_input_chars`, ideally at sentence or whitespace boundary.

Keep/remove guidance:

- Keep.
- Add `BaseStreamingTTSAdapter` or `BaseRealtimeVoiceAdapter` only if Smart Tutor moves to live streaming speech.
- Do not remove Markdown stripping; it protects TTS quality.

### `smarttutor/services/voice/config.py`

Purpose:

- Dataclasses for resolved TTS/STT provider config.

`TTSConfig` fields:

- `model`
- `provider_name`
- `adapter`
- `auth_style`
- `api_key`
- `base_url`
- `api_version`
- `extra_headers`
- `voice`
- `response_format`
- `speed`
- `max_input_chars`
- `request_timeout`

`STTConfig` fields:

- `model`
- `provider_name`
- `adapter`
- `request_style`
- `auth_style`
- `api_key`
- `base_url`
- `api_version`
- `extra_headers`
- `language`
- `request_timeout`

Constants:

- `DEFAULT_MAX_INPUT_CHARS = 4096`
- `STT_MULTIPART = "multipart"`
- `STT_BASE64_JSON = "base64_json"`

Keep/remove guidance:

- Keep.
- Extend for local engines later with fields such as `device`, `compute_type`, `sample_rate`, `model_path`, or `binary_path` only when needed.

### `smarttutor/services/voice/adapters/__init__.py`

Purpose:

- Adapter registry.

Current TTS adapters:

- `openai_compat`
- `openrouter_tts`

Current STT adapters:

- `openai_compat`

Keep/remove guidance:

- Keep.
- This is the exact place to register future Smart Tutor adapters:
  - `faster_whisper`
  - `whisper_cpp`
  - `piper`
  - `kokoro`
  - `windows_sapi`

### `smarttutor/services/voice/adapters/openai_compat.py`

Purpose:

- Implements OpenAI-compatible TTS and STT over HTTP.

TTS adapter:

- Posts JSON to `/audio/speech`.
- Payload includes:
  - `model`
  - `input`
  - `voice` when configured
  - `response_format`
  - `speed` when configured
- Returns full audio bytes.
- Maps formats to content types:
  - `mp3` -> `audio/mpeg`
  - `opus` -> `audio/opus`
  - `aac` -> `audio/aac`
  - `flac` -> `audio/flac`
  - `wav` -> `audio/wav`
  - `pcm` / `pcm16` -> `audio/pcm`

OpenRouter TTS adapter:

- First tries OpenAI-compatible `/audio/speech`.
- Falls back to chat-completions audio when needed.
- Internally reads streamed base64 audio chunks, but still returns one complete audio result to the caller.

STT adapter:

- Posts to `/audio/transcriptions`.
- Supports multipart upload style.
- Supports base64 JSON style for OpenRouter-like providers.
- Parses:
  - OpenAI-style JSON `text`
  - chat-style `choices[0].message.content`
  - raw text fallback

Keep/remove guidance:

- Keep.
- This powers both cloud and local OpenAI-compatible services.
- For Railway deployment, this should remain the primary implementation path.

### `smarttutor/services/config/provider_runtime.py`

Purpose:

- Central provider metadata and runtime resolver.

Current TTS providers:

| Provider | Default base URL | Default model | Default voice | Adapter | Local |
| --- | --- | --- | --- | --- | --- |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini-tts` | `alloy` | `openai_compat` | No |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini-tts` | `alloy` | `openrouter_tts` | No |
| Groq | `https://api.groq.com/openai/v1` | `canopylabs/orpheus-v1-english` | `autumn` | `openai_compat` | No |
| SiliconFlow | `https://api.siliconflow.cn/v1` | `FunAudioLLM/CosyVoice2-0.5B` | `FunAudioLLM/CosyVoice2-0.5B:alex` | `openai_compat` | No |
| Azure OpenAI | blank/admin-entered | `tts-1` | `alloy` | `openai_compat` | No |
| vLLM / Local | `http://localhost:8000/v1` | blank | blank | `openai_compat` | Yes |
| Custom | blank/admin-entered | blank | blank | `openai_compat` | No |

Current STT providers:

| Provider | Default base URL | Default model | Request style | Adapter | Local |
| --- | --- | --- | --- | --- | --- |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini-transcribe` | multipart | `openai_compat` | No |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/whisper-large-v3` | base64 JSON | `openai_compat` | No |
| Groq | `https://api.groq.com/openai/v1` | `whisper-large-v3-turbo` | multipart | `openai_compat` | No |
| SiliconFlow | `https://api.siliconflow.cn/v1` | `FunAudioLLM/SenseVoiceSmall` | multipart | `openai_compat` | No |
| Azure OpenAI | blank/admin-entered | `whisper-1` | multipart | `openai_compat` | No |
| vLLM / Local | `http://localhost:8000/v1` | blank | multipart | `openai_compat` | Yes |
| Custom | blank/admin-entered | blank | multipart | `openai_compat` | No |

Runtime resolution:

- Reads active profile and model under `services.tts` or `services.stt`.
- Canonicalizes provider names.
- Uses provider default base URL when profile base URL is blank.
- For local `vllm`, injects placeholder API key `sk-no-key-required` if no key exists.
- Returns `TTSConfig` or `STTConfig`.

Keep/remove guidance:

- Keep.
- Add local Smart Tutor providers to these tables when the adapters are ready.
- Do not hard-code Smart Tutor voice settings elsewhere.

### `smarttutor/services/config/model_catalog.py`

Purpose:

- Defines and normalizes service catalog shape.

Voice relevance:

- Ensures `services.tts` and `services.stt` exist.
- For TTS models, ensures `voice` exists.
- Voice settings live alongside LLM, embedding, search, image, and video provider settings.

Keep/remove guidance:

- Keep.
- Extend only if Smart Tutor needs per-student/per-class voice profiles.

### `smarttutor/services/config/test_runner.py`

Purpose:

- Settings diagnostics for provider tests.

Voice relevance:

- `_test_tts()` resolves TTS config and calls `synthesize_speech()`.
- Uses sample text: English plus Chinese.
- Returns audio bytes as base64 with content type.
- `_test_stt()` resolves STT config and calls `transcribe_audio()` with a generated WAV test clip.

Keep/remove guidance:

- Keep.
- Add local-engine diagnostic checks later:
  - binary path exists
  - model file exists
  - GPU/CPU mode usable
  - expected sample audio can be synthesized/transcribed

### `smarttutor/partners/transcription.py`

Purpose:

- Legacy/partner transcription provider using Groq Whisper API.

Important details:

- Reads `GROQ_API_KEY` from process environment.
- Posts to `https://api.groq.com/openai/v1/audio/transcriptions`.
- Uses model `whisper-large-v3`.
- Accepts a file path, not raw browser upload bytes.

Relationship to main voice system:

- Separate from `smarttutor.services.voice`.
- Does not use the central STT settings catalog.

Keep/remove guidance:

- Keep only if Smart Tutor keeps partner channels that need it.
- Prefer migrating partner transcription to `smarttutor.services.voice.transcribe_audio()` for one voice configuration system.

### `smarttutor/services/path_service.py`

Purpose:

- General filesystem path service.

Voice relevance:

- Has `get_co_writer_audio_dir()`.
- Creates `workspace/co-writer/audio`.

Relationship to chat voice:

- Not used by `/api/v1/voice/tts` or `/api/v1/voice/stt`.
- Useful only for generated/stored co-writer audio assets.

Keep/remove guidance:

- Keep if co-writer remains.
- Not required for the current chat voice loop.

## 4. Frontend Voice Files

### `web/hooks/useVoiceRecorder.ts`

Purpose:

- Browser microphone capture and backend transcription.

Flow:

1. Checks `navigator.mediaDevices.getUserMedia`.
2. Checks browser `MediaRecorder`.
3. Requests microphone permission with `{ audio: true }`.
4. Records chunks into memory.
5. On stop, builds a `Blob`.
6. Infers file extension from MIME:
   - `ogg`
   - `mp4`
   - default `webm`
7. Uploads the recording as `FormData` to `/api/v1/voice/stt`.
8. Receives `{ text }`.
9. Passes the trimmed transcript to the composer.

States:

- `idle`
- `recording`
- `transcribing`

Error messages:

- `Recording is not supported in this browser.`
- `Microphone permission denied.`
- `Transcription failed (...)`

Keep/remove guidance:

- Keep.
- Add language selection only if Smart Tutor needs multilingual class modes.
- Add VAD/chunked streaming only in a later phase.

### `web/components/chat/home/ChatComposer.tsx`

Purpose:

- Chat input surface.

Voice relevance:

- Imports `useVoiceRecorder`.
- Defines `handleTranscript(text)`.
- Appends the transcript to the existing composer text.
- Shows microphone button.
- Disables recording while an answer is streaming or transcription is in progress.
- Uses accessible `aria-label` and `title`:
  - `Record voice`
  - `Stop recording`

Keep/remove guidance:

- Keep.
- For Smart Tutor, this is where voice input can become a learner-friendly "Speak answer" control.
- Avoid rewriting the entire composer.

### `web/components/chat/home/ChatMessages.tsx`

Purpose:

- Chat message list and assistant-message controls.

Voice relevance:

- Imports `useVoiceAutoplay`.
- Creates audio playback with `new Audio(objectUrl)`.
- Speaker button posts to `/api/v1/voice/tts`.
- Receives a blob response.
- Creates an object URL.
- Plays the audio.
- Cleans up the audio object and object URL on finish/error/unmount.
- Button states:
  - loading spinner
  - stop icon while playing
  - speaker icon while idle
- Tooltip:
  - `Play aloud`
  - `Stop`
- Can autoplay freshly generated assistant replies when enabled.

Keep/remove guidance:

- Keep.
- Modify for streaming TTS only if response latency is a major issue.
- Add visible transcript/caption controls here if Smart Tutor needs accessibility-first voice.

### `web/hooks/useVoiceAutoplay.ts`

Purpose:

- Manages global and per-session autoplay preference.

Model:

- Global default stored in backend settings: `ui.voice_autoplay`.
- Session override stored in browser `sessionStorage`.
- First-play prompt stored in `sessionStorage`.

Endpoints:

- Reads `/api/v1/settings`.
- Writes `/api/v1/settings/voice-autoplay`.

Keep/remove guidance:

- Keep.
- Smart Tutor can default this off for safety/accessibility and let users opt in.

### `web/app/(utility)/settings/tts/page.tsx`

Purpose:

- TTS settings page.

Current UI:

- Page title: `Text-to-Speech`
- Describes read-aloud support.
- Uses `ServiceConfigEditor service="tts"`.
- Includes `AutoplayToggle`.

Autoplay toggle accessibility:

- Uses `role="switch"`.
- Uses `aria-checked`.
- Uses `aria-label`.

Keep/remove guidance:

- Keep.
- Rename/reword later for Smart Tutor branding only.

### `web/app/(utility)/settings/stt/page.tsx`

Purpose:

- STT settings page.

Current UI:

- Page title: `Speech-to-Text`
- Describes composer microphone transcription.
- Uses `ServiceConfigEditor service="stt"`.

Keep/remove guidance:

- Keep.
- Add local model download/status controls later only if local STT becomes part of the product.

### `web/components/settings/ServiceConfigEditor.tsx`

Purpose:

- Shared provider/profile/model editor for LLM, embedding, search, TTS, STT, image, and video generation.

Voice relevance:

- Labels `tts` as `Text-to-Speech`.
- Labels `stt` as `Speech-to-Text`.
- Shows TTS voice badge.
- Provides TTS voice input.
- Provides TTS output format select:
  - `mp3`
  - `wav`
  - `opus`
  - `aac`
  - `flac`
  - `pcm`
- Prefills provider default model for TTS/STT.
- Prefills provider default voice for TTS.
- Runs diagnostics through the backend test runner.

Keep/remove guidance:

- Keep.
- This page gives Smart Tutor provider flexibility for free.
- Add local provider-specific fields carefully; do not fork settings pages unless necessary.

### `web/components/settings/SettingsContext.tsx`

Purpose:

- Frontend settings/catalog state manager.

Voice relevance:

- `ServiceName` includes `tts` and `stt`.
- `CatalogModel` includes voice-related fields:
  - `voice`
  - `response_format`
  - `language`
- `voiceService(service)` returns true for `tts` and `stt`.
- New TTS model defaults include:
  - provider default voice
  - `response_format: "mp3"`

Keep/remove guidance:

- Keep.
- Add Smart Tutor voice policy defaults here only after backend config fields exist.

### `web/lib/settings-nav.ts`

Purpose:

- Settings navigation metadata.

Voice relevance:

- Adds `Text-to-Speech` settings nav item.
- Adds `Speech-to-Text` settings nav item.
- Uses audio/microphone icons.
- Points doc references at `data/user/settings/model_catalog.json`.

Keep/remove guidance:

- Keep.
- Rename labels only if final branding requires it.

### `web/lib/markdown-display.ts` and `web/components/visualize/VisualizationViewer.tsx`

Purpose:

- Markdown/visualization rendering.

Voice relevance:

- Allow `audio` tags in sanitized/rendered content paths.
- This is separate from chat TTS playback, which uses `new Audio()`.

Keep/remove guidance:

- Keep if Smart Tutor allows generated audio assets in answers or visualizations.

## 5. Current End-to-End Flows

### 5.1 Speech-to-Text Flow

```text
User clicks mic
  -> ChatComposer calls recorder.toggle()
  -> useVoiceRecorder starts MediaRecorder
  -> browser asks for microphone permission
  -> user speaks
  -> user clicks mic again
  -> recorder stops
  -> webm/ogg/mp4 blob is built
  -> POST /api/v1/voice/stt multipart file
  -> FastAPI reads all bytes
  -> transcribe_audio()
  -> resolve_stt_runtime_config()
  -> OpenAICompatSTTAdapter
  -> provider /audio/transcriptions
  -> transcript returned
  -> ChatComposer appends transcript to existing input
```

Key behavior:

- Dictation happens before message send.
- The user still controls when to send the transcript.
- The transcript is appended to typed text.
- There is no real-time partial transcript.

### 5.2 Text-to-Speech Flow

```text
User clicks speaker on assistant message
  -> ChatMessages POST /api/v1/voice/tts with message text
  -> FastAPI calls synthesize_speech()
  -> resolve_tts_runtime_config()
  -> strip_markdown_for_speech()
  -> OpenAICompatTTSAdapter / OpenRouterTTSAdapter
  -> provider returns audio bytes
  -> backend returns audio response
  -> browser creates object URL
  -> browser plays with new Audio(url)
```

Key behavior:

- TTS is generated per assistant message.
- TTS strips Markdown before synthesis.
- Playback is client-side.
- No audio is persisted by default.
- Autoplay can trigger this flow for new assistant replies.

## 6. Dependencies and Runtime Requirements

### Python dependencies already relevant

From `pyproject.toml` and requirements:

- `openai>=1.30.0`
- `httpx>=0.27.0`
- `python-multipart>=0.0.6`

Voice adapter detail:

- The central voice adapter uses raw HTTP through `httpx`.
- It does not require the OpenAI Python SDK for the TTS/STT calls shown here.
- `python-multipart` is needed for FastAPI upload handling.

### Frontend dependencies already relevant

No special voice package is required for the current chat voice features.

Browser APIs used:

- `navigator.mediaDevices.getUserMedia`
- `MediaRecorder`
- `Blob`
- `FormData`
- `Audio`
- `URL.createObjectURL`
- `sessionStorage`
- `CustomEvent`

### Dependencies not currently present

The current project does not include direct dependencies for:

- `whisper`
- `faster-whisper`
- `whisper.cpp`
- `piper`
- `kokoro`
- `sounddevice`
- `pyaudio`
- local VAD libraries
- local audio resampling/transcoding packages for the chat voice path

`ffmpeg` appears as a system prerequisite for math animation/video rendering, not as part of the chat voice STT/TTS path.

## 7. Environment Variables and Settings

### Current settings model

Main TTS/STT provider configuration lives in:

```text
data/user/settings/model_catalog.json
```

The active TTS/STT profile and model are resolved by:

- `resolve_tts_runtime_config()`
- `resolve_stt_runtime_config()`

Profiles can store:

- API key
- base URL
- API version
- extra headers
- provider binding

Models can store:

- model id
- voice
- response format
- language

### Voice autoplay setting

Global default:

```text
ui.voice_autoplay
```

API route:

```text
PUT /api/v1/settings/voice-autoplay
```

Default value:

```json
{
  "voice_autoplay": false
}
```

### Environment variables found

Central voice services primarily use settings catalog values, not `.env`.

Separate legacy partner transcription uses:

```text
GROQ_API_KEY
```

No voice-specific API key examples were found in `.env.example`.

Smart Tutor recommendation:

- Keep the settings catalog as the main runtime source.
- For Railway, configure provider API keys as environment variables only if the catalog loader/provider profiles are extended to read them safely.
- Do not rely on project-root `.env` files for runtime voice settings unless the runtime settings policy changes.

## 8. Cloud Voice Providers

The project currently targets OpenAI-compatible APIs. This is good for Smart Tutor because one adapter can support several providers.

Current built-in cloud choices:

- OpenAI
- OpenRouter
- Groq
- SiliconFlow
- Azure OpenAI
- Custom OpenAI-compatible endpoint

Cloud benefits:

- Fastest to deploy on Railway.
- No local model downloads.
- No GPU/CPU model management.
- Good for multi-user web deployment.
- Easier diagnostics.

Cloud tradeoffs:

- Requires API keys.
- Per-use cost.
- Audio leaves local machine unless provider has a private deployment.
- Latency depends on provider/network.

OpenAI note:

- OpenAI documents request-based speech-to-text, text-to-speech, and realtime audio workflows. Request-based APIs fit the current SmartTutor design; realtime sessions are better for live low-latency conversations.

References:

- [OpenAI Audio and Speech docs](https://developers.openai.com/api/docs/guides/audio)
- [OpenAI Text-to-Speech docs](https://developers.openai.com/api/docs/guides/text-to-speech)
- [OpenAI Speech-to-Text docs](https://developers.openai.com/api/docs/guides/speech-to-text)
- [OpenAI Realtime and Audio docs](https://developers.openai.com/api/docs/guides/realtime)

## 9. Local Voice Options for Smart Tutor

No local STT/TTS engine is currently implemented. These are future options.

### 9.1 Local STT: faster-whisper

What it is:

- Python Whisper implementation using CTranslate2.
- Designed for faster/lower-memory Whisper inference.

Fit with current architecture:

- Excellent fit for a new `BaseSTTAdapter`.
- Can accept uploaded bytes after saving to a temp file or decoding into audio.
- Can return plain transcript text through the existing `/api/v1/voice/stt` route.

Pros:

- Strong accuracy.
- Good CPU/GPU flexibility.
- Python integration is straightforward.
- Good first local STT choice for a desktop/local Smart Tutor.

Cons:

- Model files can be large.
- Needs audio decoding path.
- CPU latency may be high on low-end machines.
- Adds native/runtime complexity.

Recommended adapter name:

```text
faster_whisper
```

Reference:

- [SYSTRAN faster-whisper](https://github.com/SYSTRAN/faster-whisper)

### 9.2 Local STT: whisper.cpp

What it is:

- C/C++ Whisper implementation.
- Supports many platforms, including Windows, Linux, macOS, WebAssembly, Raspberry Pi, and Docker.

Fit with current architecture:

- Good for a subprocess-backed adapter.
- Could also run as a local OpenAI-compatible HTTP server if wrapped externally.

Pros:

- Good performance.
- Broad platform support.
- Strong fit for offline desktop usage.
- Can be packaged separately from Python dependencies.

Cons:

- Binary management is more complex.
- Need model file management.
- Need careful Windows path handling.
- Subprocess integration needs timeout/cancel handling.

Recommended adapter name:

```text
whisper_cpp
```

Reference:

- [ggml-org whisper.cpp](https://github.com/ggml-org/whisper.cpp)

### 9.3 Local TTS: Piper

What it is:

- Fast local neural TTS.
- Commonly used through ONNX voice models.

Fit with current architecture:

- Good subprocess or Python-wrapper TTS adapter.
- Can generate WAV and return it through existing `/api/v1/voice/tts`.

Pros:

- Fast local speech.
- Lightweight voices.
- Good for offline/low-cost read-aloud.
- Voice samples and many voices exist.

Cons:

- Main historical repository is archived/read-only as of October 2025 and points to moved development.
- Voice quality varies by voice.
- Less expressive than newer neural TTS systems.
- Needs voice/model file management.

Recommended adapter name:

```text
piper
```

References:

- [rhasspy/piper](https://github.com/rhasspy/piper)
- [Piper voice samples](https://rhasspy.github.io/piper-samples/)

### 9.4 Local TTS: Kokoro

What it is:

- Open-weight TTS model family around Kokoro-82M.
- Apache-licensed weights are reported by the official project/model card.

Fit with current architecture:

- Good candidate for a local Python or ONNX-backed TTS adapter.
- Also available through OpenAI-compatible wrappers, which could work with the current `openai_compat` adapter.

Pros:

- Better naturalness target than basic local TTS.
- Lightweight compared with many neural TTS systems.
- Good future Smart Tutor voice quality candidate.
- Some wrappers expose OpenAI-compatible `/audio/speech`.

Cons:

- More moving parts than Piper.
- Voice/model ecosystem is evolving.
- Need dependency and license review before bundling.

Recommended adapter names:

```text
kokoro
kokoro_openai_compat
```

References:

- [hexgrad/kokoro](https://github.com/hexgrad/kokoro)
- [Kokoro-82M model card](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro FastAPI OpenAI-compatible wrapper](https://github.com/remsky/Kokoro-FastAPI)

### 9.5 Local TTS: Windows Native TTS

What it is:

- Windows system voices through SAPI or Windows speech APIs.

Fit with current architecture:

- Possible as a Windows-only adapter.
- Good for quick offline read-aloud without model downloads.

Pros:

- No cloud API.
- No neural model downloads.
- Fast.
- Good fallback on Windows.

Cons:

- Windows-only.
- Voice quality depends on installed system voices.
- Packaging and service-account audio permissions can be awkward.
- Not ideal for Railway/Linux deployment.

Recommended adapter name:

```text
windows_sapi
```

Smart Tutor recommendation:

- Use only as an optional local fallback.
- Do not make it the main product voice.

## 10. Accessibility Assessment

Current accessibility strengths:

- Mic button has `aria-label`.
- Speaker/play button has tooltip text.
- TTS autoplay toggle uses switch semantics.
- Manual play keeps audio user-initiated by default.
- Voice autoplay defaults to off.

Current accessibility gaps:

- No live captions for generated TTS.
- No visible STT confidence or transcript review metadata.
- No keyboard shortcut visible/standardized for push-to-talk.
- No waveform, elapsed recording time, or input level indicator.
- No automatic reduced-motion/audio-respect policy beyond autoplay default.
- No per-user speech rate, voice, or language preference in the learner profile.
- No screen-reader-only status region for recording/transcribing errors beyond button title.

Smart Tutor accessibility goals:

- Keep voice optional.
- Always show text transcript.
- Never autoplay by default for new users.
- Provide clear recording, transcribing, playing, and error states.
- Add captions/transcripts for generated audio.
- Allow slower speech rate for younger learners and accessibility needs.
- Add language/accent-aware STT settings when multilingual tutoring is needed.

## 11. Performance and Scaling

Current performance behavior:

- STT uploads complete audio blob after recording stops.
- STT reads whole upload into memory.
- TTS waits for complete provider response.
- Frontend plays only after complete audio blob is received.
- No server-side cache.
- No background queue.
- No streaming chunk playback to frontend.

Implications:

- Good enough for short dictated questions and short answer read-aloud.
- Not ideal for long lectures, live tutoring calls, or real-time conversation.
- 25 MB upload cap protects the backend but still allows memory spikes under concurrent use.

Smart Tutor performance recommendations:

- Phase 1: keep request-response audio.
- Phase 2: add local engine adapters with strict timeouts and temp-file cleanup.
- Phase 3: add chunked/streaming TTS if perceived delay is high.
- Phase 4: add realtime voice sessions only if Smart Tutor truly needs live spoken dialogue.

## 12. Keep, Modify, Remove, Do Not Touch

### Keep

- `smarttutor/api/routers/voice.py`
- `smarttutor/services/voice/*`
- `smarttutor/services/config/provider_runtime.py` voice provider tables
- `smarttutor/services/config/model_catalog.py` TTS/STT service shape
- `smarttutor/services/config/test_runner.py` voice diagnostics
- `web/hooks/useVoiceRecorder.ts`
- `web/hooks/useVoiceAutoplay.ts`
- `web/components/chat/home/ChatComposer.tsx` microphone integration
- `web/components/chat/home/ChatMessages.tsx` speaker playback integration
- `web/app/(utility)/settings/tts/page.tsx`
- `web/app/(utility)/settings/stt/page.tsx`
- `web/components/settings/ServiceConfigEditor.tsx`
- `web/components/settings/SettingsContext.tsx`
- `web/lib/settings-nav.ts`

### Modify Later

- `provider_runtime.py`: add Smart Tutor local providers.
- `adapters/__init__.py`: register local adapters.
- `voice/config.py`: add optional local engine fields if needed.
- `ServiceConfigEditor.tsx`: expose local model path/device fields only after backend support exists.
- `useVoiceRecorder.ts`: add language, VAD, or streaming only when product scope requires it.
- `ChatMessages.tsx`: add streaming playback/captions if read-aloud becomes central.

### Remove Later Only If Product Scope Shrinks

- `smarttutor/partners/transcription.py`: remove only if partner integrations are removed or migrated.
- `web/lib/markdown-display.ts` audio allowance: remove only if generated audio content is forbidden.
- `web/components/visualize/VisualizationViewer.tsx` audio allowance: remove only if audio visualizations are forbidden.

### Do Not Touch During First Smart Tutor Voice Pass

- Chat orchestrator.
- Capability registry.
- Tool registry.
- RAG/knowledge-base pipeline.
- Session storage.
- Auth system.
- Main settings persistence.

Reason:

The voice system is already isolated enough. Early Smart Tutor work can be done inside the voice/settings/frontend voice modules.

## 13. Smart Tutor Target Architecture

### Recommended target

```text
Smart Tutor Chat UI
  |-- typed input
  |-- voice dictation
  |-- read-aloud
  |-- optional autoplay
  |-- captions/transcript status

Smart Tutor Backend
  |-- /api/v1/voice/stt
  |-- /api/v1/voice/tts
  |-- optional /api/v1/voice/realtime later

Voice Service
  |-- same synthesize_speech()
  |-- same transcribe_audio()
  |-- local/cloud policy resolver

Adapters
  |-- openai_compat
  |-- openrouter_tts
  |-- faster_whisper
  |-- whisper_cpp
  |-- piper
  |-- kokoro
  |-- windows_sapi
```

### Deployment profiles

#### Railway/cloud profile

Recommended:

- LLM: OpenAI or configured cloud LLM
- Embeddings: OpenAI or hosted compatible embedding provider
- STT: OpenAI/Groq/SiliconFlow
- TTS: OpenAI/OpenRouter/Groq/SiliconFlow

Why:

- Railway containers should not depend on local desktop microphones, Windows voices, or large user-managed model files.
- Cloud APIs are easier to scale and monitor.

#### Local/private profile

Recommended:

- LLM: Ollama or local OpenAI-compatible server
- Embeddings: Ollama `nomic-embed-text` or existing local embedding option
- STT: faster-whisper first, whisper.cpp second
- TTS: Piper first for simple offline read-aloud, Kokoro for better voice quality

Why:

- Privacy-first deployments benefit from local audio processing.
- Existing adapter abstraction can support this cleanly.

## 14. Four-Phase Implementation Plan

### Phase 1: Document and Stabilize Existing Voice

Goal:

- Keep current cloud voice working while rebranding toward Smart Tutor.

Work:

- Keep current `/api/v1/voice/tts` and `/api/v1/voice/stt`.
- Keep existing settings pages.
- Add user-facing Smart Tutor copy later without changing behavior.
- Add basic smoke tests around:
  - Markdown stripping
  - provider URL joining
  - STT upload size rejection
  - PCM-to-WAV conversion
- Add a short operations guide for configuring OpenAI/Groq TTS/STT.

Files:

- `smarttutor/api/routers/voice.py`
- `smarttutor/services/voice/base.py`
- `smarttutor/services/voice/__init__.py`
- `smarttutor/services/config/provider_runtime.py`
- `web/app/(utility)/settings/tts/page.tsx`
- `web/app/(utility)/settings/stt/page.tsx`

Risk:

- Low.

### Phase 2: Add Local STT/TTS Adapters

Goal:

- Support offline/local Smart Tutor voice without touching the chat UI contract.

Work:

- Add `faster_whisper` STT adapter.
- Add `piper` TTS adapter.
- Register adapters in `smarttutor/services/voice/adapters/__init__.py`.
- Add local provider specs in `provider_runtime.py`.
- Add config fields only where necessary:
  - model path
  - device
  - compute type
  - binary path for subprocess engines
- Add diagnostics for local engine availability.
- Keep cloud providers unchanged.

Files:

- `smarttutor/services/voice/adapters/faster_whisper.py`
- `smarttutor/services/voice/adapters/piper.py`
- `smarttutor/services/voice/adapters/__init__.py`
- `smarttutor/services/voice/config.py`
- `smarttutor/services/config/provider_runtime.py`
- `smarttutor/services/config/test_runner.py`
- `web/components/settings/ServiceConfigEditor.tsx`
- `web/components/settings/SettingsContext.tsx`

Risk:

- Medium.

Main risks:

- Native dependencies.
- Model downloads.
- Windows/Linux differences.
- Audio format conversion.

### Phase 3: Improve Learner Voice Experience

Goal:

- Make voice feel like a learning feature, not only a utility.

Work:

- Add recording timer and clearer recording/transcribing status.
- Add optional language selector for STT.
- Add learner-level voice preferences:
  - preferred voice
  - speech speed
  - autoplay preference
  - response language
- Add captions/transcript display for TTS playback.
- Add retry/re-record UX for bad transcripts.
- Add accessibility status text for screen readers.

Files:

- `web/hooks/useVoiceRecorder.ts`
- `web/hooks/useVoiceAutoplay.ts`
- `web/components/chat/home/ChatComposer.tsx`
- `web/components/chat/home/ChatMessages.tsx`
- `web/app/(utility)/settings/tts/page.tsx`
- `web/app/(utility)/settings/stt/page.tsx`
- possibly user/profile settings files after product model is finalized

Risk:

- Medium.

Main risks:

- UI clutter.
- Browser API differences.
- Autoplay restrictions.

### Phase 4: Optional Realtime Voice Tutor

Goal:

- Add live spoken tutoring only if Smart Tutor needs it.

Work:

- Add realtime voice endpoint or WebSocket route.
- Add chunked microphone upload or realtime provider session.
- Add streaming transcript events.
- Add interrupt/barge-in support.
- Add streaming TTS playback.
- Add session-level safety controls:
  - recording consent
  - visible mic state
  - stop-all-audio control
  - retention policy
- Add observability for latency and failures.

Files:

- new `smarttutor/api/routers/voice_realtime.py` or extend `voice.py`
- new realtime adapter interfaces under `smarttutor/services/voice/`
- `web/hooks/useVoiceRecorder.ts` or new `useRealtimeVoice.ts`
- `web/components/chat/home/ChatComposer.tsx`
- `web/components/chat/home/ChatMessages.tsx`
- session/event streaming files only if reused carefully

Risk:

- High.

Recommendation:

- Do not start here.
- Only build this after normal dictation and read-aloud are solid.

## 15. File-by-File Future Implementation Map

| File | Current role | Smart Tutor action |
| --- | --- | --- |
| `smarttutor/api/main.py` | Registers voice router | Keep |
| `smarttutor/api/routers/voice.py` | TTS/STT HTTP API | Keep; harden upload validation later |
| `smarttutor/services/voice/__init__.py` | Public facade | Keep stable |
| `smarttutor/services/voice/base.py` | Base interfaces/helpers | Keep; add streaming base only in Phase 4 |
| `smarttutor/services/voice/config.py` | Runtime config dataclasses | Extend in Phase 2 for local engines |
| `smarttutor/services/voice/adapters/__init__.py` | Adapter registry | Add local adapters |
| `smarttutor/services/voice/adapters/openai_compat.py` | Cloud/OpenAI-compatible adapter | Keep |
| `smarttutor/services/config/provider_runtime.py` | Provider tables and config resolver | Add local provider specs |
| `smarttutor/services/config/model_catalog.py` | Catalog schema normalization | Keep; extend only for new config fields |
| `smarttutor/services/config/test_runner.py` | Provider diagnostics | Add local diagnostics |
| `smarttutor/partners/transcription.py` | Legacy Groq partner STT | Migrate or remove only if partners are removed |
| `web/hooks/useVoiceRecorder.ts` | Mic capture/upload | Keep; enhance UX in Phase 3 |
| `web/hooks/useVoiceAutoplay.ts` | Autoplay state | Keep |
| `web/components/chat/home/ChatComposer.tsx` | Mic button and transcript append | Keep; add better recording status |
| `web/components/chat/home/ChatMessages.tsx` | TTS playback button/autoplay | Keep; add captions/streaming later |
| `web/app/(utility)/settings/tts/page.tsx` | TTS settings | Keep; rebrand copy later |
| `web/app/(utility)/settings/stt/page.tsx` | STT settings | Keep; rebrand copy later |
| `web/components/settings/ServiceConfigEditor.tsx` | Provider/model form | Extend carefully for local fields |
| `web/components/settings/SettingsContext.tsx` | Settings state/types | Extend carefully for local fields |
| `web/lib/settings-nav.ts` | Settings navigation | Keep |
| `web/lib/markdown-display.ts` | Allows audio content | Keep if generated audio remains |
| `web/components/visualize/VisualizationViewer.tsx` | Allows audio in visualizations | Keep if media learning remains |

## 16. Final Recommendation

For Smart Tutor, keep the current voice architecture and evolve it in place.

Recommended near-term stack:

- Cloud deployment on Railway:
  - Use existing OpenAI-compatible TTS/STT path.
  - Start with OpenAI or Groq for STT.
  - Start with OpenAI/OpenRouter/Groq for TTS depending on cost and voice quality.
- Local/private desktop deployment:
  - Add `faster_whisper` for STT.
  - Add `piper` as the first simple local TTS.
  - Add Kokoro later if better naturalness is required.

Do not build realtime voice first. The existing dictation plus read-aloud model is simpler, safer, more accessible, and easier to deploy. Realtime voice should be Phase 4 after Smart Tutor's core learning flows are stable.

