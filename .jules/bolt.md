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

## 2026-03-08 - Lazy Version and Standard Library Module Import Deferral
**Learning:** `importlib.metadata` eagerly loads heavy submodules (`email`, `pathlib`, `zipfile`, `csv`, `re`, `inspect`, `typing`) adding ~83ms import overhead on CLI startup. Replacing top-level `import importlib.metadata` in `google.agents.cli.__init__` with PEP 562 module `__getattr__` and using `@click.version_option(package_name="google-agents-cli")` defers version resolution until explicitly requested. Deferring cold-path imports of `tomllib`, `traceback`, and `logging` removes all eager standard library overhead.
**Action:** Use PEP 562 module `__getattr__` for `__version__` export and Click's `package_name` parameter to keep version lookup lazy on CLI startup.
