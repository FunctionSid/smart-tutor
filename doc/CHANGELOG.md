# Changelog

All notable changes and verification records for the Smart Tutor project are documented here.
Entries are appended in chronological order. Past entries are never modified.

---

## 2026-09-03 - Phase 1: Repository Consolidation and Documentation Setup

### What was changed
- Reconfigured Git remote `origin` to `https://github.com/FunctionSid/smart-tutor.git`.
- Configured local Git credential helper to `manager` for Windows compatibility.
- Cleaned up empty stray `docs/` folder to adhere to the single `doc/` documentation path rule.
- Restructured commits from clean fork root into logical reviewable groups:
  1. Root configuration, packaging, and scripts (`chore: project root configuration, tooling, and environment setup`).
  2. Backend core services and CLI (`feat(backend): core smarttutor engine and services`).
  3. Web application frontend and assets (`feat(frontend): web application source, components, and assets`).
  4. Unit and integration tests (`test: unit and integration test suites`).
  5. Documentation consolidation (`docs: establish single source of truth and changelog`).
- Established `doc/SMART_TUTOR_STATE.md` as the single living source of truth.
- Established `doc/CHANGELOG.md` as the running work log.

### What was verified
- Remote URL updated and verified via `git remote -v`.
- `git status --ignored --short` confirmed `.gitignore` cleanly excludes `data/`, `.venv`, `node_modules`, and build caches.
- No exposed credentials or secrets found in staged or modified files.
- `data/knowledge_bases/kb_config.json` verified to hold existing KB `audit_science_sqp_20260829`.

### What broke / Known issues
- `/knowledge` main content rendering issue flagged for fix in Phase 2.
- `faster-whisper` diagnostic timeout flagged for investigation in Phase 2.
- `personas.count.suffix` untranslated string flagged for fix in Phase 2.
