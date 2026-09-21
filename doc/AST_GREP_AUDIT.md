# ast-grep (sg) Code Audit: Deep-Tutor

This document contains structural code analysis of the deep-tutor codebase using ast-grep (sg). It is written for developers and AI coding agents to pinpoint bug-prone patterns, anti-patterns, and opportunities for cleanup and hardening.

---

## 1. Executive Summary

- Tool used: ast-grep 0.45.3 (Syntax-aware AST matching)
- Target project: D:\project\deep-tutor
- Languages analyzed: Python (smarttutor/), TypeScript (web/)
- Key findings:
  1. Broad Exception Handling: Over 1,100 occurrences of except Exception:, some silently passing without logging or retrying.
  2. Empty Catch / Pass Statements: Multiple locations where errors are swallowed with pass (Python) or empty catch blocks (TypeScript).
  3. Subprocess Invocations: Direct process spawning across Windows/POSIX with PowerShell and cmd execution paths.
  4. SQL Parameterization: SQLite queries in sqlite_store.py properly bind values using ?, with dynamic set clauses that require column allowlisting.
  5. Environment Variable Reliance: Over 40 runtime settings and API keys retrieved via os.environ.get() that need fallback guards.

---

## 2. Findings by Category

### A. Silent Error Swallowing (except Exception: pass)

#### Critical files to review:
1. smarttutor/services/llm/provider_core/codebuddy_provider.py:
   - Lines 115-116: except BaseException: pass
   - Lines 144-145: except Exception: pass
   - Lines 363-364: except Exception: pass
   - Lines 553-554: except Exception: pass
   - Recommendation: Replace BaseException with specific exceptions. Add logger.debug or logger.warning with exc_info=True.

2. smarttutor/runtime/launcher.py:
   - Lines 103-104, 109-110, 115-116, 161-162, 168-169, 425-426, 434-435, 560-561, 709-710, 1253-1254.
   - Recommendation: The launcher swallows process inspection and termination errors. Wrap with debug-level logging so failed process shutdowns are visible.

3. smarttutor/services/rag/pipelines/modes.py:
   - Lines 37-38: except Exception: pass
   - Recommendation: Ensure defensive fallbacks do not mask misconfigured RAG providers.

4. smarttutor/partners/channels/telegram.py & weixin.py:
   - Lines 511-512, 1023 in telegram.py: except Exception: pass
   - Lines 1060, 1234 in weixin.py: pass
   - Recommendation: Channel messaging errors should at least log an error or increment a telemetry counter.

---

### B. Frontend Empty Catch Blocks (TypeScript)

- File: web/lib/theme.ts (Lines 36-48): Catches localStorage access error and silently ignores. Acceptable fallback for private browsing.
- Console Errors in Frontend:
  - web/lib/persistence.ts (Lines 83-85): localStorage quota exceeded
  - web/lib/unified-ws.ts (Line 255): WebSocket not connected
  - web/components/notebook/useNotebookSelection.ts (Lines 49, 79): Failed to fetch notebooks
  - Recommendation: Route UI network and storage errors through an accessible toast or banner component so screen readers (NVDA/JAWS) announce errors.

---

### C. Subprocess Executions

- smarttutor/services/sandbox/runner/server.py (Line 236): Executes sandboxed user commands. Correctly uses preexec_fn for POSIX and explicit argument parsing.
- smarttutor/runtime/launcher.py (Lines 894-905, 941-954): Executes PowerShell commands for process inspection. Ensure timeout bounds handle cases where WMI or PowerShell hangs on busy Windows systems.
- smarttutor/services/llm/provider_core/codebuddy_provider.py (Line 803): Spawns cmd.exe /d /s /c on Windows. Verify arguments are escaped.

---

### D. SQLite Database Execution Patterns

- File: smarttutor/services/session/sqlite_store.py
  - High coverage of parameterized queries with ? bindings.
  - Lines 1937-1940: UPDATE notebook_entries SET {set_clause} WHERE id = ?
    - Recommendation: Validate that every column in set_clause comes from an explicit allowlist of known schema column names.
  - Lines 2105-2108: WHERE id IN ({placeholders}) properly interpolates only ? placeholders; values are bound as tuples.

---

### E. Environment Variable Resolution

- High frequency across settings, sandbox config, and LLM providers.
- Key keys used: SMARTTUTOR_MODE, CODEBUDDY_API_KEY, GROQ_API_KEY, KRUTRIM_API_KEY, SMARTTUTOR_RUNNER_ALLOWED_WORKDIRS, HF_HOME, DOCLING_CACHE_DIR, DOCLING_ARTIFACTS_PATH.
- Recommendation: Centralize environment variable reads into smarttutor/services/config/ with clear schema validation.

---

## 3. Quick Reference ast-grep Commands for AI Agents

When working on deep-tutor, other agents can run these exact commands:

1. Find all bare pass statements in Python:
   ast-grep run -p 'pass' --lang python smarttutor

2. Find broad exception blocks in a specific service:
   ast-grep run -p 'except Exception:' --lang python smarttutor/services/rag

3. Find subprocess executions:
   ast-grep run -p 'subprocess.$FUNC($$$ARGS)' --lang python smarttutor

4. Find dynamic SQL string queries:
   ast-grep run -p '$CONN.execute($$$ARGS)' --lang python smarttutor/services/session/sqlite_store.py

5. Find frontend React error logs:
   ast-grep run -p 'console.error($$$ARGS)' --lang ts web/components

---

## 4. Priorities for Future AI Sessions
1. Add logging to silent except Exception: pass in codebuddy_provider.py and launcher.py.
2. Ensure dynamic SQL set_clause in sqlite_store.py enforces a strict column whitelist.
3. Centralize scattered os.environ.get calls into typed settings schemas.
