# Palette's Journal - Critical Learnings Only

## 2026-03-07 - Defaulting CLI Login to Interactive Mode
**Learning:** For single-purpose interactive commands (such as `agents-cli login`), requiring the user to explicitly pass `-i` or `--interactive` is an unnecessary hurdle that results in predictable usage errors. Defaulting to interactive mode eliminates the boilerplate while retaining the option to opt-out via `--no-interactive` or run programmatically.
**Action:** Default single-purpose interactive setup/login commands to interactive mode by default and support standard `--no-interactive` overrides.
