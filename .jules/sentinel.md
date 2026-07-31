# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Dynamic Case-Insensitive Log Redaction with Boundary Safeguards
**Vulnerability:** Initial static sanitization rules were easily bypassed by alternative parameter casings, comma-separated option values, and missed newer secret variable prefixes or key patterns (e.g. passwords, credentials, tokens).
**Learning:** Hardcoded exact strings for secrets are fragile. Case-insensitive key checks and support for sub-structures like comma-separated parameters are required to prevent leakages under edge-cases. However, loose substring matching on short terms like 'pat' or 'pass' can lead to widespread false positive redactions (e.g. `--path` or `--compat` being redacted), necessitating component boundary checks.
**Prevention:** Use a standardized check of options and arguments that splits component names on hyphens/underscores to match short credentials exactly, and split lists on commas or key-value separators (like `=` and `:`) to sanitize complex structured arguments recursively.
