# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager CLI Start Dependency Loading
**Learning:** Eagerly importing third-party dependencies (such as `yaml`) at module top-level of files (such as `_project.py` or `_skills_check.py`) that are imported on the CLI command startup path adds a significant latency overhead (~24ms). By lazily importing `yaml` inside functions that actually parse YAML documents, we avoid loading the library on standard command dispatch and reduce CLI startup import time by ~15%.
**Action:** Always use lazy imports for heavy third-party packages inside the functions where they are executed instead of at the module top-level.
