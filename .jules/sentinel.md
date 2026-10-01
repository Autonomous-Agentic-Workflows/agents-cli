# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-28 - Unsafe `shell=True` Subprocess Execution for Environment Scripts
**Vulnerability:** Sourcing external environment setup scripts via `subprocess.run(f"source {VERTEX_ENV}", shell=True, executable="/bin/bash")` exposed the application to potential command injection vulnerabilities. In addition, environment variables exported in subshells do not persist back to Python's parent process environment.
**Learning:** Shell script sourcing commands using `shell=True` should be avoided when loading environment variables for Python sub-processes.
**Prevention:** Read environment files directly in Python with file I/O and populate the target process environment dictionary (`env`) explicitly without invoking shell subprocesses.
