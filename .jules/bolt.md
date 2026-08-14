# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager Imports in Global Paths
**Learning:** Even when a module is imported only to read metadata or perform quick checks, eager imports of heavy libraries (e.g. `requests`, `rich`, `packaging`, `yaml`) inside those modules severely degrade CLI startup time (adding ~130ms+ overhead even on fast-paths where the checks are not due). Moving them to local imports inside specific check functions cuts startup latency in half.
**Action:** Defensively lazy-import any heavy external libraries in modules that are imported during CLI startup or fast-path checks.

## 2026-03-07 - Non-Blocking Background CLI Update Checking
**Learning:** Checking for PyPI updates by making a blocking HTTP request during CLI startup adds significant, unpredictable network latency (often 100ms to 2s+ depending on connection) directly to the CLI execution path. Spawning a detached background process using standard library `urllib.request` to write the latest version to a local cache file entirely removes this latency, allowing the CLI to start up instantly by reading from the cache.
**Action:** Always offload update checks and remote status queries in CLIs to a detached background process that writes to a local cache file, and read from that cache during startup.
