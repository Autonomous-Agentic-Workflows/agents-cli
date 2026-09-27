# Sentinel Journal

## 2026-08-22 - Comma-Separated Secret Redaction in Subprocess Execution
**Vulnerability:** Subprocess arguments containing comma-separated `KEY=VALUE` environment variable lists (e.g., `--update-env-vars FOO=bar,OPENAI_API_KEY=sk-...`) either failed to redact generic third-party API keys/tokens or completely masked entire parameter strings.
**Learning:** Checking whole argument strings against exact env var names misses third-party provider keys (like `OPENAI_API_KEY`, `BEARER_TOKEN`, `PRIVATE_KEY`) and fails to parse comma-delimited environment variable lists cleanly.
**Prevention:** In `_runner.py`'s `redact_cmd`, parse comma-separated `KEY=VALUE` segments individually against generic sensitive keyword patterns (`API_KEY`, `TOKEN`, `BEARER`, `SECRET`, `PASSWORD`, `PASS`, `PAT`, `PRIVATE_KEY`, `CREDENTIAL`) to achieve precise, non-leaking sanitization.

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.
