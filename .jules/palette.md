# Palette's Journal - Critical Learnings Only

## 2026-03-07 - Color-Coded CLI Message Tagging
**Learning:** Raw text block listings in local terminal execution output (e.g., `agents-cli run`) lack a visual hierarchy, making it hard to distinguish user prompts, agent responses, file assets, and internal tool call flows. Standardizing and color-coding tags (green for agents/authors, yellow for user prompts, cyan for files, bold blue for tool calls, and magenta for tool responses) drastically reduces cognitive load, allowing developers to debug agent reasoning sequences instantly.
**Action:** When designing interactive or streaming CLI output views, always partition output components with high-contrast, semantic colors matching their logical role.
