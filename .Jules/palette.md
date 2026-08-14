# Palette's Journal

A log of critical UX and accessibility learnings and best practices for the Google Agents CLI project.

## 2026-07-24 - [CLI Output Rich Styling & Readability]
**Learning:** Terminal CLI tools can feel dry and cognitively heavy when presenting configuration parameters in plain unstyled text. Introducing subtle color coding, typography weights, and structured visual groups (using tools like `rich`) dramatically improves visual scanning, screen reader focus clarity, and overall developer delight.
**Action:** Use structured labels with distinctive coloring (such as cyan for paths/names, green for active status, and yellow for alerts) to make key information instantly recognizable in standard output, while carefully retaining unchanged `--json` format outputs for reliable programmatic integrations.

## 2026-07-25 - [Implicitly Interactive Commands Defaults]
**Learning:** For terminal commands that are inherently interactive (such as `login`), requiring users to explicitly supply interactive flags like `-i` / `--interactive` is a source of unnecessary cognitive load and user frustration. Defaulting to interactive mode provides a seamless, error-free path for first-time users, while programmatic scripts can use `--non-interactive` to override the behavior.
**Action:** Always default inherently interactive commands to interactive mode, allowing seamless execution while providing `--non-interactive` alternative flags for automation.
