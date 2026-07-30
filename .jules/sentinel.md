# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Enhanced Dynamic Redaction & False Positive Prevention
**Vulnerability:** Redaction was static, case-sensitive, and missed many generic credential formats (e.g., lowercase flags, generic passwords, tokens, or custom credentials inside nested lists). Simple substring checks on terms like `pat` or `pass` would cause massive false positives (e.g., masking `PATH` or `COMPAT_MODE`).
**Learning:** Robust dynamic redactors must combine case-insensitive substring matching for long-form terms (`api_key`, `secret`, `password`, `credential`) with component boundary matching (`_` or `-` boundaries) for short-form terms (`pat`, `pass`).
**Prevention:** Always validate option arguments individually and handle recursive/delimiter-separated lists (like comma-separated key-value pairs) recursively or individually rather than using simple global search/replace.
