# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Robust Case-Insensitive Multi-Format Key-Value Redaction
**Vulnerability:** The previous subprocess argument redactor relied on rigid hardcoded matchers for specific option flag names and exact environment variables, which could be bypassed via case variation, alternative hyphen/underscore separators (e.g., `--API-KEY`), or when sensitive keys appeared inside comma-separated parameter lists.
**Learning:** Multi-variable and comma-separated option lists (such as `foo=bar,api_key=secret,baz=qux`) bypassed standard simple prefix lookups. Short credential patterns like `pat` or `pass` required component-boundary word splitting (`-` or `_` delimiters) to prevent false-positive masking on common words like `path`, `pattern`, `compat`, `template`, `patch`, or `passenger`.
**Prevention:** Implement a unified tokenizer that parses separate key-value structures and comma-separated option lists. Normalize and split key strings on component boundaries to perform precise, robust, and false-positive-free credential/secret redaction.
