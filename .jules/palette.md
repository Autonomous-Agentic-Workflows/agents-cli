# Palette's UX Journal 🎨

## 2026-03-05 - Defaulting Command Interactivity to Reduce CLI Friction
**Learning:** For command-line interface commands that inherently require human interaction (such as authentication or wizard-based setup flows), forcing users to explicitly pass an interactive flag (e.g., `-i` or `--interactive`) creates unnecessary cognitive friction and errors. Users expect commands like `login` to run interactively immediately. By defaulting to interactive mode on local terminals while offering an opt-out (like `--no-interactive`) for automation, we minimize user friction without sacrificing scriptability.
**Action:** When designing or reviewing CLI commands that guide users through a setup, login, or configuration process, always default to interactive execution on user terminals, and design non-interactive alternatives via standard flags/environment variables rather than requiring explicit interaction flags.
