# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Dynamic and Case-Insensitive Log Redaction with Boundary Safeguards
**Vulnerability:** Static and hardcoded secret logging patterns in `redact_cmd` failed to capture case-insensitive options, comma-separated configuration options, and varied environment variable patterns, leading to potential leakages of model and integration credentials.
**Learning:** Naive substring-matching for short terms like `pat` or `pass` results in disruptive false positives on safe common variables (e.g. `path`, `pattern`, `compat`, `bypass`). Splitting keys on snake_case and kebab-case component boundaries (underscore or hyphen) is a highly effective security pattern that balances robust dynamic matching with zero false positives.
**Prevention:** Always parse CLI options and environment variables dynamically, split sub-components of comma-separated parameter lists, and validate short secret identifiers strictly against component boundaries.
