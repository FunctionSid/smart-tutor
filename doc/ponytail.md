# Ponytail

Ponytail is a Codex plugin/skill used for coding work in this project. It pushes
Codex toward the smallest useful implementation: question whether work is needed,
reuse existing project code, prefer the standard library or native platform
features, avoid new dependencies, and keep diffs short.

## Current Setup

- Status: installed and available in the current Codex environment.
- Installed version: `4.9.0`.
- Plugin path: `C:\Users\Sourabh\.codex\plugins\cache\ponytail\ponytail\4.9.0`.
- Skill path: `C:\Users\Sourabh\.codex\plugins\cache\ponytail\ponytail\4.9.0\skills\ponytail\SKILL.md`.
- Project configuration: no in-repository Ponytail configuration was found before
  this file was added.
- Default override: `PONYTAIL_DEFAULT_MODE` is not set.
- User config override: no config file was found at
  `C:\Users\Sourabh\AppData\Roaming\ponytail\config.json`.

Because there is no override, Ponytail uses its default mode: `full`.

## What Ponytail Changes

Ponytail changes Codex's coding behavior, not the Smart Tutor application
runtime. It is not imported by the frontend or backend and is not part of the
deployed product.

For coding tasks, Ponytail applies this order of preference:

1. Do nothing if the requested work does not need to exist.
2. Reuse existing code in the repository.
3. Use the language standard library.
4. Use native platform features.
5. Use an already-installed dependency.
6. Prefer one clear line over a larger abstraction.
7. Only then add the minimum code that works.

For bug fixes, Ponytail favors fixing the root cause once, after checking callers
of the affected function or module. It also favors deletion over addition, the
fewest changed files, and no speculative scaffolding.

When a deliberate shortcut has a known ceiling, developers should mark it with a
small `ponytail:` comment that names the limit and the trigger for revisiting it.

## Modes

- `lite`: build what was asked and mention a simpler alternative when relevant.
- `full`: default mode; apply the full YAGNI, reuse, standard library, native,
  and minimum-diff ladder.
- `ultra`: deletion-first mode; challenges requirements before building and
  removes avoidable code aggressively.
- `off`: disables Ponytail behavior for the session.

Ponytail can be deactivated with `stop ponytail`, `normal mode`, or
`/ponytail off`. It can be resumed with `/ponytail`.

## Commands

- `/ponytail`: switch to `full` mode when no level is specified.
- `/ponytail lite`: switch to `lite` mode.
- `/ponytail full`: switch to `full` mode.
- `/ponytail ultra`: switch to `ultra` mode.
- `/ponytail off`: turn Ponytail off.
- `/ponytail-help`: show the Ponytail quick reference.
- `/ponytail-review`: review current changes for over-engineering only.
- `/ponytail-audit`: audit the whole repository for over-engineering only.
- `/ponytail-debt`: list existing `ponytail:` comments as a debt ledger.
- `/ponytail-gain`: show Ponytail benchmark impact ranges. These are benchmark
  medians, not project-specific savings.

## How To Verify It Is Active

Developers can verify the local installation with:

```powershell
Test-Path C:\Users\Sourabh\.codex\plugins\cache\ponytail\ponytail\4.9.0\skills\ponytail\SKILL.md
```

They can verify the available command metadata with:

```powershell
Get-ChildItem C:\Users\Sourabh\.codex\plugins\cache\ponytail\ponytail\4.9.0\commands
```

Inside Codex, `/ponytail-help` should show the quick reference, and `/ponytail`
should enable the default `full` mode. In normal use, active Ponytail behavior
shows up as smaller diffs, fewer new abstractions, fewer new dependencies, and
shorter implementation explanations.

## Developer Guidance

When using Ponytail in this project:

- Read the existing Smart Tutor code before adding new code.
- Reuse local helpers, registries, services, and API patterns.
- Prefer changing one shared root-cause path over patching multiple symptoms.
- Do not add dependencies for logic that the existing stack or standard library
  can handle.
- Keep feature work scoped to the requested behavior.
- For non-trivial logic, leave one small runnable check or test when practical.
- Preserve explicit requirements, trust-boundary validation, data-loss handling,
  security checks, and accessibility basics.

## Limitations

Ponytail does not guarantee correctness, security, performance, test coverage, or
production readiness. It is not a linter, formatter, test runner, type checker,
or CI gate. It does not replace code review. It also does not override explicit
project requirements; if Smart Tutor needs a real feature, validation layer,
database migration, or user-facing state, Ponytail should make that work smaller,
not pretend it is unnecessary.
