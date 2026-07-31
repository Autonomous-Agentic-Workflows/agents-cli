# Sentinel Journal

🛡️ Sentinel: Guardian of the Codebase

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** The CLI's subprocess runner was only redacting GitHub-specific credentials (`--github-pat`, `GITHUB_PAT`, `GH_TOKEN`, `GITHUB_TOKEN`, `GITHUB_APP_KEY`) in executed commands before printing them to the console. It was failing to redact crucial Google Cloud and Gemini credentials like `GEMINI_API_KEY` and `GOOGLE_API_KEY`, potentially leaking sensitive API keys to the standard output and logs when those commands were printed during execution.
**Learning:** Security redaction lists should always cover the core authentication vectors of the application itself. Since `agents-cli` is primarily designed for Google AI Studio and Vertex AI platforms, missing `GEMINI_API_KEY` and `GOOGLE_API_KEY` left a major defense-in-depth gap.
**Prevention:** Maintain a comprehensive and centralized list of sensitive environment variable keys and option flags (e.g. `--api-key`, `--access-token`) in command-logging helpers, and implement thorough automated tests to verify credential masking across all core variables.
