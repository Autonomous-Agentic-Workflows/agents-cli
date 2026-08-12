# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-25 - Safe Keyword Substring Matching in Log Redaction
**Vulnerability:** Naive substring matching for short sensitive keywords (e.g. `pat` for `GITHUB_PAT` or `pass` for `MY_PASSWORD`) causes false positive redactions of harmless arguments like `--patch`, `--passenger`, and `--bypass`, degrading logging usability.
**Learning:** Subprocess log redactors must distinguish between substring matches within word boundaries (e.g., kebab-case and snake_case components) and substring matches spanning normal words.
**Prevention:** Standardize string separators (e.g., replace hyphens with underscores) and split keys/variables into component parts before performing equality checks on very short sensitive words.
