# Smart Tutor — Current Status

Audit date: 2026-08-29  
Workspace: `D:\project\deep-tutor`  
Backend stack found: FastAPI  
Frontend stack found: Next.js  
Overall status: PARTIAL, with the local core learning and voice paths working

This is the authoritative current status for the Smart Tutor workspace. It records only what was inspected, implemented, or tested in this machine state.

## 1. Product Purpose

Smart Tutor is intended to be an accessible AI tutoring app where a learner can upload or attach study material, ask questions, receive grounded explanations, practice and revise topics, and optionally use speech input and spoken replies.

The practical target is:

- Chat with OpenAI or local/Ollama models.
- Use documents and knowledge bases for grounded answers.
- Keep embeddings separate from chat model selection.
- Support speech input and speech output through configured voice engines.
- Preserve accessibility for keyboard users and NVDA users.

## 2. Current Architecture

Frontend: Next.js app under `web/`, with workspace chat, Settings pages, knowledge UI, memory UI, and learning surfaces.

Backend: FastAPI app under `smarttutor/api`, with routers for settings, voice, knowledge, sessions, tools, memory, and learning features.

LLM: Provider/runtime configuration is stored in `data/user/settings/model_catalog.json`. OpenAI and Ollama/local providers are supported through the Smart Tutor LLM runtime.

Knowledge/RAG: Knowledge bases live under `data/knowledge_bases`. The verified path in this audit is the LlamaIndex provider through `RAGService`.

Document ingestion: `KnowledgeBaseInitializer` copies source files into a KB `raw/` folder and invokes the selected RAG provider. Incremental uploads use `DocumentAdder`.

Chunking: The verified LlamaIndex pipeline parses and chunks documents during index creation. The exact chunking parameters are provider-specific and not redesigned in this pass.

Embeddings: Active local embedding provider is Ollama `nomic-embed-text`, detected as 768 dimensions.

Vector database/index: The verified KB created provider version folders for the LlamaIndex path and was queryable through `RAGService.search`.

Chat: Chat UI is reachable at `http://localhost:3782/home`; backend session/runtime paths are present. Full browser upload-to-cited-answer testing remains incomplete.

STT: Voice input endpoint is `/api/v1/voice/stt`. Active implementation uses global Python plus `faster-whisper` through a subprocess adapter.

TTS: Voice output endpoint is `/api/v1/voice/tts`. Active implementation uses global `edge-tts` through a subprocess adapter. OpenAI TTS, gTTS, Windows System.Speech, Piper, and pyttsx3 adapters/provider entries are also implemented or audited as described below.

Memory: Existing memory surfaces and services are present. Full product-level memory workflow was not retested in this voice audit.

Revision: Learning/revision UI and services exist. Full revision workflow was not retested in this voice audit.

Practice: Quiz/practice-related frontend and backend code exists. Full practice workflow was not retested in this voice audit.

Progress: Knowledge indexing progress and learning progress surfaces exist. Knowledge duplicate/progress metadata was tested.

## 3. AI Providers

OpenAI:

- Configuration status: CONFIGURED locally through ignored runtime catalog.
- Active chat model: `gpt-4.1`.
- API key handling: stored in `data/user/settings/model_catalog.json`, not in frontend code, source docs, `.env`, or `.env.example`.
- Tested status: PASS through Smart Tutor LLM diagnostic and runtime call.

Ollama:

- Configuration status: CONFIGURED for embeddings and available for local chat.
- Local models discovered included `qwen3.5:27b`, `qwen3:8b`, `qwen3:4b`, `llama3:latest`, and `nomic-embed-text:latest`.
- Tested status: PASS for Ollama API discovery, PASS for Smart Tutor local LLM connectivity using `qwen3:4b`, PASS for embeddings using `nomic-embed-text`.
- Caveat: tested local chat model did not obey an exact-output instruction cleanly, so local model quality depends on the selected model.

Embedding models:

- Embeddings are separate from chat model selection.
- Active embedding model: Ollama `nomic-embed-text`.
- Detected dimension: 768.

## 4. Local Launch

Status: PASS

Verified launch files:

- `start-smart-tutor.bat`
- `set-openai-key.bat`
- `set-openai-key.ps1`

`start-smart-tutor.bat` activates `.venv`, installs the local package if needed, installs frontend dependencies if missing, starts `smarttutor start --dev`, prints URLs, and opens the frontend.

Live check:

- Frontend `http://localhost:3782`: PASS
- Backend `http://127.0.0.1:8001`: PASS
- Backend knowledge health: PASS

No project-root `.env` file is required for the current local setup. Runtime settings are stored under ignored `data/user/settings/*.json`.

## 5. RAG And Document Ingestion

Status: PASS for the LlamaIndex path

Live audit KB: `audit_science_sqp_20260829`

Input document:

- Existing local file: `data/user/workspace/chat/attachments/.../9b675b882fa5_Science-SQP.pdf`
- File type: PDF
- Size: 960,352 bytes

Result:

- KB initialization: PASS
- Provider: `llamaindex`
- Indexed raw file count: 1
- Stored initial file hash count: 1
- RAG search: PASS
- Retrieved sources: 3
- Retrieved grounded content included the Science Class X sample paper header and instructions.

Duplicate handling:

- Re-adding the same PDF staged 0 files.
- Duplicate count: 1.
- Skipped count: 1.
- Fix implemented: initial KB creation now records `metadata.file_hashes`, so duplicate detection works immediately after creating a KB.

Not live-tested in this pass:

- GraphRAG
- LightRAG
- PageIndex
- IMA
- external LightRAG server

## 6. Voice Environment

Status: PASS for global faster-whisper STT and global Edge TTS

Important correction: the Smart Tutor `.venv` does not own the Whisper/TTS packages. The global Python installation does. Smart Tutor now invokes selected global tools by subprocess instead of installing duplicate packages into `.venv`.

Smart Tutor venv:

- Python: `D:\project\deep-tutor\.venv\Scripts\python.exe`
- Local Whisper/TTS packages: not installed in `.venv`

Global Python/PATH:

- Global Python: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\python.exe`
- `faster-whisper` 1.2.1: INSTALLED, IMPLEMENTED, CONFIGURED, TESTED, WORKING
- `ctranslate2` 4.7.1: INSTALLED, TESTED by import/discovery, not a direct Smart Tutor STT provider
- `openai-whisper` 20250625: INSTALLED, but NOT WORKING because global Numba rejects NumPy 2.5
- `whisper-timestamped` 1.15.9: INSTALLED, but NOT WORKING for the same OpenAI Whisper/Numba/NumPy issue
- `piper-tts` 1.4.2: INSTALLED
- `edge-tts` 7.2.8: INSTALLED, IMPLEMENTED, CONFIGURED, TESTED, WORKING
- `pyttsx3` 2.99: INSTALLED, IMPLEMENTED, import-tested, but synthesis failed on this machine
- `gTTS` 2.5.4: INSTALLED, IMPLEMENTED, live synthesis tested, requires internet

## 7. STT

Selected implementation:

- Provider: `faster_whisper`
- Adapter: `global_faster_whisper`
- Global executable used: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\python.exe`
- Package owner: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\Lib\site-packages\faster_whisper\__init__.py`
- Model selected: `tiny`
- Language: `en`

Invocation:

Smart Tutor writes uploaded audio to a temporary file, runs the configured global Python executable in a subprocess, imports `faster_whisper.WhisperModel`, transcribes the file, emits JSON, and returns the transcript through `/api/v1/voice/stt`.

Real STT test:

- Recording source: generated local WAV via Windows System.Speech, saved as `data/user/voice_audit/recorded_system_speech_probe.wav`
- STT facade result: `Smart Tudor Local Voice Recording Test.`
- Running API endpoint result: `Smart Tudor Local Voice Recording Test.`
- Status: WORKING
- Caveat: this was not a physical microphone test. Codex could not physically press/record from the user's microphone, so microphone hardware/browser permission is implemented but not physically verified.

Manual microphone diagnostic:

1. Open `http://localhost:3782/home`.
2. Press the chat microphone button.
3. Allow microphone permission.
4. Speak a short sentence.
5. Press the button again to stop.
6. Confirm the transcript appears in the composer and can be edited before sending.

## 8. TTS

Selected implementation:

- Provider: `edge_tts`
- Adapter: `global_edge_tts`
- Global executable used: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\Scripts\edge-tts.EXE`
- Package owner: `C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\Lib\site-packages\edge_tts\__init__.py`
- Voice selected: `en-US-AriaNeural`
- Output: `audio/mpeg`
- Internet requirement: Edge TTS uses Microsoft Edge online voices and should not be called offline/local-only.

Invocation:

Smart Tutor runs the global `edge-tts` executable in a subprocess, writes an MP3 in a temporary directory, reads the bytes, and returns them from `/api/v1/voice/tts`.

Real TTS tests:

- Chat answer generated: `Photosynthesis is important because it produces oxygen and food, sustaining most life on Earth.`
- Edge TTS output: `data/user/voice_audit/chat_answer_edge_tts.mp3`, 38,880 bytes
- Playback attempt: PASS, duration 6.48 seconds
- Running API endpoint after final restart: PASS, `audio/mpeg`, 20,448 bytes

Other engines:

- Windows System.Speech: IMPLEMENTED and TESTED through Smart Tutor adapter; produced `data/user/voice_audit/windows_system_speech_adapter.wav`, 145,972 bytes.
- Piper: IMPLEMENTED and installed, but no `.onnx` plus `.onnx.json` voice model pair was found. Status: Installed — no voice models found. Smart Tutor will not pretend Piper voices are available and will not download voices automatically.
- pyttsx3: IMPLEMENTED and installed, but real synthesis failed even with explicit `sapi5`; status is installed but not working/verified for synthesis on this machine.
- gTTS: IMPLEMENTED and TESTED; produced `data/user/voice_audit/gtts_test.mp3`, 28,800 bytes. Requires internet and is not offline.
- OpenAI TTS: IMPLEMENTED and TESTED with a temporary catalog using the existing OpenAI key; produced `data/user/voice_audit/openai_tts_check.mp3`, 61,056 bytes. The key was not printed or written to docs.

Azure Speech:

- Not used.
- Not added.
- Not part of the Smart Tutor target.

## 9. Windows Voices

Status: PASS for dynamic discovery

Smart Tutor diagnostics discovers installed Windows voices dynamically through PowerShell 7 and `System.Speech`.

Final live diagnostics reported 18 Windows voices. Useful voices include:

- Microsoft Heera
- Microsoft Ravi
- Microsoft Hemant
- Microsoft Kalpana
- Microsoft David
- Microsoft Hazel
- Microsoft Zira

Settings/provider support:

- `windows_speech` provider is registered.
- `pyttsx3` provider is registered.
- Windows voices are available through diagnostics for future UI dropdown use.

## 10. Voice Diagnostics

Status: PASS

New endpoint:

- `GET /api/v1/voice/capabilities`

It reports:

- global Python path
- STT capabilities
- TTS capabilities
- installed/configured/implemented/tested/working booleans
- executable path
- package owner path
- package version
- discovered Windows voices
- discovered Piper voice model pairs

Final live endpoint summary:

- `faster-whisper`: installed/configured/implemented/tested/working
- `Whisper CLI`: installed but not working
- `ctranslate2`: installed
- `Windows System.Speech`: installed/implemented/tested/working, 18 voices
- `Piper`: installed/implemented/tested, no voice models found
- `Edge TTS`: installed/configured/implemented/tested/working
- `pyttsx3`: installed/implemented/import-tested, synthesis not verified/failed
- `gTTS`: installed/implemented, live synthesis tested outside endpoint
- `OpenAI TTS`: implemented and tested with temporary catalog

## 11. Chat Voice UX

Status: PARTIAL with backend path working

Playback:

- Chat message speaker button calls `/api/v1/voice/tts`.
- It creates a browser `Audio` object from the returned blob and plays it.
- TTS endpoint works with the active Edge TTS provider.
- Playback errors now announce a screen-reader-visible error instead of failing silently.

Recording:

- Chat composer microphone button uses `MediaRecorder`.
- It requests browser microphone permission.
- It records audio chunks.
- It sends the audio to `/api/v1/voice/stt`.
- It appends the returned transcript into the composer.
- The user can edit the transcript before sending.

Accessibility updates:

- Recording started is announced.
- Recording stopped and transcribing is announced.
- Transcription complete is announced.
- Transcription failed is announced.
- TTS generating/playing/failure states are announced.

Not physically verified:

- Real microphone hardware capture.
- Browser permission dialog with NVDA.
- Full manual keyboard-only recording flow.

## 12. Settings

Status: PARTIAL but improved

Implemented:

- TTS providers include Edge TTS, Windows System.Speech, Piper, pyttsx3, gTTS, OpenAI-compatible providers, and local OpenAI-compatible servers.
- STT providers include global faster-whisper and OpenAI-compatible providers.
- Local/global voice providers hide API key fields.
- Local/global voice providers label the connection field as a global executable/Python path instead of a generic HTTP base URL.
- TTS/STT Settings copy no longer presents Azure Speech as a target.
- AI chat model selection remains separate from embeddings.

Still missing:

- A polished ordinary-user voice settings screen with dependent dropdowns for engine, voice, language, and speed.
- A frontend dropdown fed directly by `/api/v1/voice/capabilities` for Windows voices and Piper voices.
- Manual NVDA review of Settings.

## 13. Accessibility

Status: PARTIAL

Confirmed/implemented:

- Buttons have accessible names for record/play controls.
- Recording, transcription, TTS loading, TTS playing, and TTS failure states use screen-reader announcements.
- Knowledge upload progress has polite live status.
- Toast viewport uses `role="status"` and `aria-live="polite"`.

Not completed:

- Manual NVDA test.
- Full keyboard-only acceptance test.
- Color contrast audit.
- Browser microphone permission dialog audit.

## 14. Tests Run

Status: PASS for focused suites

Python:

```text
91 passed in 4.05s
```

Covered:

- Voice facade and HTTP routes
- Global faster-whisper adapter
- Global Edge TTS adapter
- Global Piper missing-model behavior
- Global pyttsx3 adapter wiring
- Global gTTS adapter wiring
- Voice diagnostics
- Settings provider metadata
- Provider runtime config

Frontend:

```text
npx tsc --noEmit
```

Result: PASS

Node tests:

```text
npm run test:node -- settings llm-options-transport
```

Result: PASS, 589 tests

Earlier verification in this workspace also passed:

- Larger focused Python suite: `133 passed`
- Knowledge/provider/upload suite: `115 passed`
- Knowledge-focused suite: `22 passed`
- Frontend lint: passed with pre-existing warnings

## 15. Files Changed

Code/test changes:

- `smarttutor/knowledge/initializer.py`
- `smarttutor/services/config/provider_runtime.py`
- `smarttutor/services/voice/adapters/__init__.py`
- `smarttutor/services/voice/adapters/global_tools.py`
- `smarttutor/services/voice/diagnostics.py`
- `smarttutor/api/routers/settings.py`
- `smarttutor/api/routers/voice.py`
- `tests/knowledge/test_kb_directory_layout.py`
- `tests/services/test_voice.py`
- `tests/services/test_voice_diagnostics.py`
- `tests/api/test_settings_router.py`
- `tests/api/test_voice_routes.py`
- `web/app/(utility)/settings/tts/page.tsx`
- `web/app/(utility)/settings/stt/page.tsx`
- `web/components/settings/SettingsContext.tsx`
- `web/components/settings/ServiceConfigEditor.tsx`
- `web/hooks/useVoiceRecorder.ts`
- `web/components/chat/home/ChatComposer.tsx`
- `web/components/chat/home/ChatMessages.tsx`

Documentation:

- `doc/SMART_TUTOR_STATUS.md`

Local runtime data:

- `data/user/settings/model_catalog.json`
- `data/user/voice_audit`
- `data/knowledge_bases/audit_science_sqp_20260829`

Local runtime data is user data and should remain ignored by Git.

## 16. Remaining Work

Before calling Smart Tutor complete as a polished end-user tutoring product:

- Physically test microphone capture in the browser.
- Run NVDA through record, transcribe, edit, send, play aloud, and Settings workflows.
- Add frontend voice capability panels/dropdowns fed by `/api/v1/voice/capabilities`.
- Add Piper voice model directory selection if Piper should be a first-class offline option.
- Decide whether to keep pyttsx3 despite current synthesis failure on this machine.
- Run the complete browser RAG workflow: attach PDF, index, ask, receive grounded answer with citations.
- Run full repository test/lint suite and a fresh secret scan before any public push.

## 17. Final Verdict

Status: PARTIAL

Smart Tutor is locally runnable and the core local foundation is operational:

document → parse/index → embed → retrieve → chat model → STT/TTS-capable runtime.

Voice is now substantially more usable: active STT uses global faster-whisper, active TTS uses global Edge TTS, diagnostics distinguish installed/configured/implemented/tested/working, and the chat UI announces voice states more accessibly.

The product is not yet fully finished because physical microphone/NVDA testing and a polished ordinary-user voice Settings flow remain open.
