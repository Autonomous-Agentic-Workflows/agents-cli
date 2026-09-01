# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-09-01 - Avoid shell=True When Sourcing Environment Variables File
**Vulnerability:** Invoking `subprocess.run(f"source {VERTEX_ENV}", shell=True)` created a potential shell injection risk if the file path or script contents were user-modifiable or maliciously crafted.
**Learning:** Using `shell=True` to execute shell scripts or source environment files is unsafe when environment variables can be parsed directly using Python string parsing or file reading.
**Prevention:** Parse shell script `KEY=VALUE` and `export KEY=VALUE` definitions safely using pure Python file handling rather than executing shell subshells via `subprocess.run(..., shell=True)`.
