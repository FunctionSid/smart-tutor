# SmartTutor CLI Skill

> Teach your AI agent to configure, manage, and use SmartTutor — an intelligent learning platform — entirely through the command line.

## When to Use

Use this skill when the user wants to:
- Set up or configure SmartTutor
- Chat with SmartTutor or run a capability (deep solve, quiz generation, deep research, visualize, math animation, mastery path)
- Create, manage, or search knowledge bases
- Create, manage, or run Partners (IM-connected companions)
- Search, install, or manage skills from a hub (ClawHub)
- Inspect or maintain interactive Books
- View or manage learning memory, sessions, or notebooks
- Start the SmartTutor API server or the full Web app

## Prerequisites

- Python 3.11+
- SmartTutor installed: `pip install smarttutor` for the full Web app, `pip install smarttutor-cli` for CLI-only, or `pip install -e .` from a source checkout
- Run `smarttutor init` for first-time interactive setup. It walks a guided wizard (ports → LLM → embedding → search → review) and writes the same settings as the Web Settings page under `data/user/settings`. Add `--cli` to skip the ports step for CLI-only use, or `--home <path>` to target a specific workspace.

## Commands

### Chat & Capabilities

```bash
# Interactive REPL
smarttutor chat
smarttutor chat --capability deep_solve --kb my-kb --tool rag --tool web_search

# One-shot capability execution
smarttutor run chat "Explain Fourier transform"
smarttutor run deep_solve "Solve x^2 = 4" --tool rag --kb textbook
smarttutor run deep_question "Linear algebra" --config num_questions=5
smarttutor run deep_research "Attention mechanisms" --kb papers --config mode=report --config depth=standard
smarttutor run visualize "Plot the unit circle"
smarttutor run math_animator "Visualize a Fourier series"

# Capabilities accepted by `run` / `chat -c`:
#   chat, deep_solve, deep_question, deep_research, visualize, math_animator, mastery_path

# Options for `run`:
#   --session <id>         Resume existing session
#   --tool/-t <name>       Enable tool (repeatable)
#   --kb <name>            Knowledge base (repeatable)
#   --notebook-ref <ref>   Notebook reference, "<notebook_id>:<rec1>,<rec2>" (repeatable)
#   --history-ref <id>     Referenced session id (repeatable)
#   --language/-l <code>   Response language (default: en)
#   --config <key=value>   Capability config (repeatable)
#   --config-json <json>   Capability config as JSON
#   --format/-f <fmt>      Output format: rich | json (default: rich)
```

`smarttutor chat` accepts the same `--session / --tool / --kb / --notebook-ref / --history-ref / --language / --config / --config-json` options, plus `--capability/-c <name>` to set the initial capability.

**Tools** for `--tool` / `-t`: user-toggleable tools are `brainstorm`, `web_search`, `paper_search`, `reason`, `geogebra_analysis`, `imagegen`, and `videogen`. Context-gated tools (`rag`, `code_execution`, `read_source`, `web_fetch`, `github`, `ask_user`, …) auto-mount when their context is present, but can also be force-enabled with `--tool`. Run `smarttutor plugin list` for the full registered set.

### Knowledge Bases

```bash
smarttutor kb list [--format rich|json]              # List all knowledge bases
smarttutor kb info <name>                            # Show knowledge base details (JSON)
smarttutor kb create <name> --doc file.pdf           # Create from documents (--doc/-d repeatable)
smarttutor kb create <name> --docs-dir ./papers      # ...or from a directory of documents
smarttutor kb add <name> --doc more.pdf              # Add documents incrementally
smarttutor kb search <name> "query text" [--mode hybrid] [--format rich|json]
smarttutor kb set-default <name>                     # Set as default KB
smarttutor kb delete <name> [--force]                # Delete a knowledge base
```

### Partners

Partners are IM-connected learning companions (the former "TutorBot").

```bash
smarttutor partner list                              # List all partners
smarttutor partner create <id> -n "My Tutor"         # Create and start a new partner
#   -n/--name <text>   Display name
#   -s/--soul <md>     Soul markdown (the persona)
#   -m/--model <id>    Model override
smarttutor partner start <id>                        # Start a partner
smarttutor partner stop <id>                         # Stop a running partner
```

### Skills

Install and manage skills, including packages from external hubs (ClawHub).
Hub refs use `<hub>:<slug>[@version]` (the hub prefix defaults to `clawhub`).

```bash
smarttutor skill search "flashcards" [--hub clawhub] [--limit 10]
smarttutor skill install clawhub:some-skill[@1.2.0] [--name local-name] [--force] [--allow-unverified]
smarttutor skill list                                # List local skills (with hub provenance)
smarttutor skill remove <name>                       # Remove a user-layer skill
```

### Books

Maintenance commands for the BookEngine (authoring/reading is via the Web app).

```bash
smarttutor book list                                 # List all books (flags stale pages)
smarttutor book health <book_id>                     # Inspect KB drift + log.md health
smarttutor book refresh-fingerprints <book_id>       # Re-snapshot KB fingerprints
```

### Memory

```bash
smarttutor memory show [<target>]    # target: L3 (all global docs, default) | L2 (all surfaces) | a doc name (e.g. profile, chat)
smarttutor memory clear [<target>]   # target: all (default) | trace (all L1) | a surface name (clears that surface's L1)
#   --force/-f   Skip confirmation
```

### Sessions

```bash
smarttutor session list [--limit 20]                 # List sessions
smarttutor session show <id> [--format rich|json]    # View session messages
smarttutor session open <id>                         # Resume session in the REPL
smarttutor session rename <id> --title "..."         # Rename a session
smarttutor session delete <id>                       # Delete a session
```

### Notebooks

```bash
smarttutor notebook list                             # List notebooks
smarttutor notebook create <name> [--description "..."]
smarttutor notebook show <notebook_id> [--format rich|json]
smarttutor notebook add-md <notebook_id> <file.md> [--title "..."] [--type chat|question|research|solve]
smarttutor notebook replace-md <notebook_id> <record_id> <file.md>
smarttutor notebook remove-record <notebook_id> <record_id>
```

### Providers

```bash
smarttutor provider login openai-codex               # OAuth login for OpenAI Codex
smarttutor provider login github-copilot             # Validate an existing Copilot auth session
```

### System

```bash
smarttutor config show                               # Print resolved configuration
smarttutor plugin list                               # List registered tools and capabilities
smarttutor plugin info <name>                         # Show a tool/capability's schema + availability
smarttutor serve [--host 0.0.0.0] [--port 8001] [--reload]   # Start the API server
smarttutor start [--home <path>]                     # Launch backend + frontend together
smarttutor init [--cli] [--home <path>]              # Create/update workspace settings
```

## REPL Slash Commands

Inside `smarttutor chat`, use these:

| Command | Effect |
|:---|:---|
| `/quit` | Exit REPL |
| `/session` | Show current session id |
| `/status` | Print the current REPL state |
| `/new` or `/clear` | Start a new session context |
| `/regenerate` or `/retry` | Re-run the last user message |
| `/tool on\|off <name>` | Toggle a tool |
| `/cap <name>` | Switch capability |
| `/kb <name>\|none` | Set or clear knowledge base |
| `/history add <id>` / `/history clear` | Manage history references |
| `/notebook add <ref>` / `/notebook clear` | Manage notebook references |
| `/show last\|<n>` | Expand a captured tool result or thinking block |
| `/refs` | Show all active references |
| `/config show\|set\|clear` | Manage capability config |

## Typical Workflows

**First-time setup:**
```bash
cd SmartTutor
pip install -e .
smarttutor init        # Interactive guided setup (add --cli for CLI-only)
```

**Daily learning:**
```bash
smarttutor chat --kb textbook --tool rag --tool web_search
```

**Build a knowledge base from documents:**
```bash
smarttutor kb create physics --doc ch1.pdf --doc ch2.pdf
smarttutor run chat "Explain Newton's third law" --kb physics --tool rag
```

**Generate quiz questions:**
```bash
smarttutor run deep_question "Thermodynamics" --kb physics --config num_questions=5
```

**Run the full Web app locally:**
```bash
smarttutor start       # backend + frontend; Ctrl+C to stop
```
