# Palette's Journal

A log of critical UX and accessibility learnings and best practices for the Google Agents CLI project.

## 2026-07-24 - [CLI Output Rich Styling & Readability]
**Learning:** Terminal CLI tools can feel dry and cognitively heavy when presenting configuration parameters in plain unstyled text. Introducing subtle color coding, typography weights, and structured visual groups (using tools like `rich`) dramatically improves visual scanning, screen reader focus clarity, and overall developer delight.
**Action:** Use structured labels with distinctive coloring (such as cyan for paths/names, green for active status, and yellow for alerts) to make key information instantly recognizable in standard output, while carefully retaining unchanged `--json` format outputs for reliable programmatic integrations.
