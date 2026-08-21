# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-24 - Pinning NPX Package Executions to Prevent Supply Chain Risks
**Vulnerability:** Unpinned `npx -y skills` execution in fallback skill searches and legacy skill detection allowed downloading and executing arbitrary `latest` npm packages instead of the pinned/verified package version.
**Learning:** `SKILLS_NPX_PACKAGE` ("skills@1.4.8") was introduced to pin package versions, but secondary checks in `_skills_check.py` and `cmd_setup.py` were still invoking unpinned `["npx", "-y", "skills", ...]`.
**Prevention:** Always use the `SKILLS_NPX_PACKAGE` constant across all `npx` subprocess calls interacting with npm packages to prevent supply chain execution risks.
