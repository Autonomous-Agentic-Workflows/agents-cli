# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-05 - Lazy-Importing Heavy Dependencies in CLI Entrypoints
**Learning:** Eagerly importing heavy third-party modules like `yaml` or `requests` at the top level of entry points or utilities (e.g., `_project.py`, `_skills_check.py`, `version.py`) introduces a severe startup penalty on every single CLI invocation. For example, `yaml` takes ~23ms and `requests` takes ~85ms of pure import time. Together with transitive dependencies like `urllib3`, this adds ~108ms (nearly 50% of total latency!) of pure overhead to the hot path, even for simple commands or `--help`. Deferring these to local scopes inside the specific functions where they are executed eliminates this latency completely.
**Action:** Always lazy-import heavy dependencies locally inside functions in CLI entrypoints, particularly when those functions are rate-limited or only executed on specific commands.

## 2026-03-06 - Eager Imports in Global Paths
**Learning:** Even when a module is imported only to read metadata or perform quick checks, eager imports of heavy libraries (e.g. `requests`, `rich`, `packaging`, `yaml`) inside those modules severely degrade CLI startup time (adding ~130ms+ overhead even on fast-paths where the checks are not due). Moving them to local imports inside specific check functions cuts startup latency in half.
**Action:** Defensively lazy-import any heavy external libraries in modules that are imported during CLI startup or fast-path checks.
