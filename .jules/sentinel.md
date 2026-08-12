# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Case-Insensitive Credential Masking in CLI Subprocesses
**Vulnerability:** Command redactors that match options and environment variables strictly in uppercase or lowercase fail to mask sensitive credentials when mixed-case formats are used, leaving credentials exposed in logs.
**Learning:** Hardcoded environment variable lists like `GEMINI_API_KEY` are bypassed if variables are supplied as mixed-case/lowercase (e.g., `gemini_api_key=...`) or if options use variations like `--PASSWORD` or custom credentials like `--access-token`.
**Prevention:** Always normalize command arguments to lowercase before comparing them against lists of sensitive options or environment variables, and actively block general patterns like `password`, `token`, and `client_secret`.
