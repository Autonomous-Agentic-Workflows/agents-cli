## 2026-03-04 - [Defaulting CLI Commands to Interactive Mode]
**Learning:** In CLI applications, forcing users to explicitly pass flags (like `--interactive` or `-i`) to initiate standard command flows is a common friction point and a bad user experience. When a user runs a command whose purpose is interactive (like `login` or `setup`), the command should default to interactive mode unless run in a scripting/non-interactive context. The option to disable interactive behavior should still be provided via flags (like `--no-interactive`), but should not be the hurdle to getting started.
**Action:** Always design user-centric CLI workflows to be interactive by default, using `--no-interactive` flags to override default behavior rather than requiring `--interactive` or `-i` to proceed.

## 2026-03-04 - [Color-Coding Terminal Output Tags in CLI Stream]
**Learning:** Monochrome stream outputs in conversational or agentic CLI sessions increase cognitive load when identifying speaker transitions, file artifacts, or tool invocations. Color-coding tag prefixes (`[user]:`, `[agent]:`, `[file:]`, `[tool_call:]`, `[tool_response:]`) provides immediate visual structure and hierarchy without cluttering output.
**Action:** Always apply semantic terminal color styling (`click.secho`) to structured event tags in CLI outputs to help users visually segment prompts, responses, and tool executions.
