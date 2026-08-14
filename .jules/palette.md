# Palette's Journal - Critical UX & Accessibility Learnings

## 2026-03-05 - Default Interactive Flow for Primary CLI Actions
**Learning:** Forcing users to supply an explicit interactive flag (such as `-i` or `--interactive`) to run a command whose sole purpose is to perform a guided/interactive setup (like `login` or `setup`) introduces unnecessary friction and increases cognitive load. The primary user flow should work seamlessly out-of-the-box with sensible defaults, while still allowing non-interactive or automated environments to override this behavior (e.g. via `--no-interactive`).
**Action:** When designing interactive CLI commands, default to interactive execution, auto-detect non-interactive TTY if possible, and allow `--no-interactive` flags to override, avoiding strict flag requirements for normal interactive use.
