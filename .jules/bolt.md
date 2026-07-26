# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager Imports of Heavy Core Libraries
**Learning:** Importing heavy packages (`requests`, `rich.console`, `yaml`, `packaging`) or instantiating heavy classes (like `Console()`) at the module top-level of files (like `_project.py` or `version.py`) that are loaded on *every* CLI startup introduces massive latency (~400ms+ of import overhead), even for lightweight commands like `--help` or `info` that don't actually use those features.
**Action:** Enforce lazy-imports inside functions/methods for any heavy dependency that is not strictly required by the module's primary export when loaded at CLI startup.
