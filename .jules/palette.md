# Palette's Journal — Critical UX Learnings

This journal is a repository of critical UX/accessibility learnings discovered while working on this repository.

## 2026-02-18 - [CLI Run Output Visual Hierarchy]
**Learning:** Terminal outputs displaying multi-turn agent execution with file attachments, tool calls, and tool responses become extremely difficult to read and parse when printed as raw, monochrome text. Adding a clean, color-coded visual hierarchy (yellow for user, green for agent, cyan for files, bold blue for tool calls, and magenta for tool responses) makes the execution path dramatically more intuitive, pleasant to follow, and accessible to parse visually.
**Action:** Always prioritize creating visual hierarchy in CLI / terminal outputs by color-coding user vs. system vs. tool actions, ensuring standard Click-based styling API is used so that it degrades gracefully in monochrome or non-interactive terminals.
