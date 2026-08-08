# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager Imports in Global Paths
**Learning:** Even when a module is imported only to read metadata or perform quick checks, eager imports of heavy libraries (e.g. `requests`, `rich`, `packaging`, `yaml`) inside those modules severely degrade CLI startup time (adding ~130ms+ overhead even on fast-paths where the checks are not due). Moving them to local imports inside specific check functions cuts startup latency in half.
**Action:** Defensively lazy-import any heavy external libraries in modules that are imported during CLI startup or fast-path checks.

## 2026-03-07 - Non-Blocking Background CLI Update Checking
**Learning:** Synchronous network operations (e.g., querying PyPI for updates via `requests.get`) on the CLI startup path introduce heavy, unpredictable latency blocks (up to 2 seconds or timeout length). We can achieve completely non-blocking update checks by instantly reading the latest known version from a local cache file on startup, and asynchronously spawning a detached background process (via `popen_resolved_detached`) using Python's standard `urllib.request` to update the cache when the check interval is due.
**Action:** Always offload non-critical network checks (such as update/telemetry pings) on CLI startup to non-blocking background detached processes and read from local cached/stamp states.
