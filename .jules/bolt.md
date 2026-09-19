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

## 2026-03-08 - Deferring importlib.metadata via PEP 562 Module __getattr__ and Click package_name
**Learning:** Top-level `import importlib.metadata` in package `__init__.py` or `@click.version_option(version=__version__)` triggers distribution resolution across `sys.path` on CLI startup, adding ~35-40ms latency and eagerly loading `importlib.metadata` and `inspect`. Using PEP 562 `__getattr__` for `__version__` and passing `package_name="google-agents-cli"` to `@click.version_option` defers metadata lookup until `--version` or `__version__` is explicitly accessed.
**Action:** Avoid eager top-level `importlib.metadata` imports in `__init__.py` and use Click's `package_name` parameter or lazy properties for version metadata.
