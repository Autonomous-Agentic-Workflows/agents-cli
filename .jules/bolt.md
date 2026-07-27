# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - CLI Startup Lazy-Import Optimization
**Learning:** Deferring heavy third-party imports (such as `requests`, `rich`, `packaging`, and `yaml`) from global module scope to local function-level scopes can drastically reduce CLI cold-start overhead. In this codebase, doing so for version and skills checks cut CLI import startup latency by nearly 300 ms (a 414x speedup on version utility import).
**Action:** Never import heavy external libraries at the module level in CLI entry points or functions executed on every startup.
