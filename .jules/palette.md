## 2026-03-01 - Initializing Visual Audit Log
**Learning:** Initiated the visual audit log for documenting UX and accessibility findings in google-agents-cli.
**Action:** Follow the guidelines to document real user feedback and specific design learnings as discoveries are made.

## 2026-03-01 - Default CLI Login to Interactive Mode
**Learning:** Command-line interfaces that require a verbose interactive option flag (like `-i`) to initiate interactive authentication are less intuitive and error-prone for first-time developers. Defaulting the login command to interactive mode aligns with standard developer workflows and CLI patterns, while keeping an option to disable interactivity (e.g. `--no-interactive`) preserves non-interactive CI/automation usage.
**Action:** When designing CLI authentication or setup flows, prefer interactive-by-default behavior with non-interactive override flags to optimize first-time developer onboarding.
