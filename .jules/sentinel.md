# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Dynamic and Tokenized Subprocess Log Redaction
**Vulnerability:** Static, exact-match redaction rules for command-line arguments and environment variables failed to catch sensitive inputs like `--db-password`, `--hf-token`, or inline credentials within comma-separated lists.
**Learning:** Hardcoded option checks cannot scale with custom/third-party integrations. Flexible, case-insensitive heuristic classification of tokens coupled with recursive sub-parameter parsing is required for thorough log safety.
**Prevention:** Implement recursive, pattern-based/tokenized value scanning inside `redact_cmd` for general keywords (`token`, `password`, `secret`, `api-key`, `pat`, `credential`) while explicitly ignoring non-sensitive suffix structures (`-path`, `-pattern`, `-template`, `-key-id`).
