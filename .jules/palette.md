# Palette's Journal - UX & Accessibility Learnings

## 2026-03-31 - [Interactive CLI Defaults]
**Learning:** Forcing users to pass explicit interactive flags (like `-i` or `--interactive`) to naturally interactive CLI commands (like `login`) is a common UX papercut that creates friction and leads to usage errors. Designing CLI commands to be interactive by default, while supporting flag overrides (such as `--no-interactive`) for automated/programmatic scripts, provides a smooth out-of-the-box developer experience.
**Action:** When designing or refactoring CLI commands that involve user choices or prompts, make them interactive by default, and use boolean options (e.g., `--interactive/--no-interactive`) to gracefully support automated contexts.
