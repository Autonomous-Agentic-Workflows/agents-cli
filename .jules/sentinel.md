# Sentinel Journal

## 2026-09-18 - Shell Execution and Command Injection via `source` Subprocess
**Vulnerability:** Shell script loading via `subprocess.run(f"source {VERTEX_ENV}", shell=True, executable="/bin/bash")` invoked a subshell (`shell=True`), exposing the CLI to arbitrary command injection risks if the script path or content contained unsanitized commands.
**Learning:** Invoking shell scripts using `shell=True` to set environment variables is both insecure and ineffective (subshell environment changes are lost when the process terminates).
**Prevention:** Parse key-value environment variable definitions directly into a target `os.environ` dictionary in Python without invoking a shell process (`shell=True`).

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.
