# Sentinel Journal

## 2026-07-24 - API Key and Secret Redaction in Command Subprocesses
**Vulnerability:** Command arguments logged or printed during subprocess invocation (e.g. CLI operations) did not mask Google and Gemini API keys or --api-key options, potentially leaking sensitive credentials to console and CI logs.
**Learning:** While GitHub PATs/tokens were redacted in `_runner.py`, other cloud and model credentials like `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `--api-key` were overlooked in log output sanitization.
**Prevention:** Ensure all sensitive environment variables and flag arguments used by the CLI have robust, automated string/regex sanitization inside `_runner.py`'s `redact_cmd` before logging.

## 2026-07-24 - Command Injection Risk in Shell Script Sourcing
**Vulnerability:** Sourcing shell configuration files via `subprocess.run(f"source {VERTEX_ENV}", shell=True)` created a potential command injection vector and failed to propagate environment variable exports to child process execution contexts.
**Learning:** Using `shell=True` with string formatting is vulnerable to command injection if file paths contain spaces or shell metacharacters. Furthermore, running `source` in a subshell without capturing `env` stdout discards exported environment variables.
**Prevention:** Avoid `shell=True` when sourcing environment scripts. Use parameterized `/bin/bash` calls like `["/bin/bash", "-c", 'source "$1" && env', "_", script_path]` to safely capture and parse exported environment variables into Python's process `env` mapping.
