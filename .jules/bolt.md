# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager Imports in Global Paths
**Learning:** Even when a module is imported only to read metadata or perform quick checks, eager imports of heavy libraries (e.g. `requests`, `rich`, `packaging`, `yaml`) inside those modules severely degrade CLI startup time (adding ~130ms+ overhead even on fast-paths where the checks are not due). Moving them to local imports inside specific check functions cuts startup latency in half.
**Action:** Defensively lazy-import any heavy external libraries in modules that are imported during CLI startup or fast-path checks.

## 2026-03-07 - Non-Blocking Background CLI Update Checking
**Learning:** Performing blocking synchronous network requests (like PyPI queries via `requests`) during CLI tool startup heavily impacts performance, adding up to 2 seconds of latency on slow/offline connections. Caching the latest known version and offloading actual network queries to a detached background subprocess (using `sys.executable` with standard library `urllib.request` to avoid heavy import overhead) eliminates startup latency completely while still keeping the user fully informed.
**Action:** Always utilize local cache files for slow remote resources, and schedule asynchronously spawned background checks using standard library modules (like `urllib`) to keep startup paths entirely non-blocking.
