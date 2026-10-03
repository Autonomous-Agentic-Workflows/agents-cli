# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Unsafe Shell Invocation for Environment Sourcing
**Vulnerability:** Invoking `subprocess.run(f"source {VERTEX_ENV}", shell=True)` introduced shell command injection risk while failing to propagate environment variables to the parent process or downstream commands.
**Learning:** Sourcing shell scripts in a child process via `shell=True` creates a temporary child process whose environment modifications vanish on exit, while exposing the execution context to shell metacharacter injection.
**Prevention:** Parse key-value environment file definitions directly in Python without invoking a shell or subshell execution with `shell=True`.
