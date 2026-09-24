# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-24 - Subprocess `shell=True` Command Injection Risk
**Vulnerability:** Invoking shell scripts or sourcing environment files via `subprocess.run` with `shell=True` introduces command injection risks if file paths contain shell metacharacters.
**Learning:** Shell script sourcing (`source script.sh`) in a subprocess subshell also fails to export environment variables into the parent process or child process context.
**Prevention:** Parse environment key-value pairs directly from configuration/script files in Python rather than delegating shell file sourcing to `subprocess.run(..., shell=True)`.
