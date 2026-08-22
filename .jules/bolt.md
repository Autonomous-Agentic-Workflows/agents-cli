# Bolt's Journal - Critical Learnings Only

## 2026-03-05 - Local Skills Fast-Path Optimization
**Learning:** During development or local checkouts, the global skills path `~/.agents/skills` is often absent. As a result, the CLI falls back to calling `npx skills list --json` on every skills check or CLI start. This subprocess execution takes ~1.3 seconds, introducing a heavy latency penalty on CLI commands. Adding local `cwd / "skills"` and `project_root / "skills"` to the fast-path search resolves this beautifully.
**Action:** Always include local workspace/project paths in fast-path checks for dependencies/plugins to avoid fallback subprocesses.

## 2026-03-06 - Eager Imports in Global Paths
**Learning:** Even when a module is imported only to read metadata or perform quick checks, eager imports of heavy libraries (e.g. `requests`, `rich`, `packaging`, `yaml`) inside those modules severely degrade CLI startup time (adding ~130ms+ overhead even on fast-paths where the checks are not due). Moving them to local imports inside specific check functions cuts startup latency in half.
**Action:** Defensively lazy-import any heavy external libraries in modules that are imported during CLI startup or fast-path checks.

## 2026-03-07 - Cross-Platform Paths in Detached Inline Subprocesses
**Learning:** When spawning detached Python background processes running inline python code via `python -c "..."` on Windows systems, unescaped backslashes in raw filesystem paths (e.g. from `Path.home()`) cause python compilation `SyntaxError`s when interpolated into strings.
**Action:** Always convert local filesystem `Path` objects to POSIX-style paths using `.as_posix()` before interpolating them into inline subprocess commands.

## 2026-03-08 - Eager Heavy SDK Imports in CLI Command Modules
**Learning:** `google.agents.cli.deploy.cmd_deploy` imported `agent_runtime.py` at module top-level, which eagerly imported Vertex AI and GCP Resource Manager SDKs (`vertexai`, `google.cloud.resourcemanager_v3`, `google.iam.v1`). This loaded over 3,000 submodules whenever `cmd_deploy` was imported (e.g. during `--help` or command discovery), causing a massive ~8.5-second latency delay. Deferring imports to runtime execution paths and moving lightweight helper functions (`parse_secrets`) to `_utils.py` reduced `agents-cli deploy --help` latency from ~28s down to ~0.33s.
**Action:** Never import submodules at top-level if they pull in heavy cloud vendor SDKs; move them to local function imports within execution paths.
