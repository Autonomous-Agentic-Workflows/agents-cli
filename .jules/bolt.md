# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager Imports in Global Paths
**Learning:** Even when a module is imported only to read metadata or perform quick checks, eager imports of heavy libraries (e.g. `requests`, `rich`, `packaging`, `yaml`) inside those modules severely degrade CLI startup time (adding ~130ms+ overhead even on fast-paths where the checks are not due). Moving them to local imports inside specific check functions cuts startup latency in half.
**Action:** Defensively lazy-import any heavy external libraries in modules that are imported during CLI startup or fast-path checks.

## 2026-03-07 - Non-Blocking Update Checking via Detached Background Process
**Learning:** Synchronous network queries performed on CLI startup (even with tight timeouts) degrade execution speed and introduce a potential multi-second delay if network latency is high or PyPI is unreachable. Offloading checking to a cached version on startup, and spawning a detached background process (via standard library's `urllib`) to update the cache only when the check interval is due, eliminates all network blocking from the main CLI execution path.
**Action:** Never run blocking synchronous network I/O during CLI startup; use file caches and spawn detached background helper processes to retrieve network updates.
