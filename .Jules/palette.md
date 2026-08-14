# Palette's Journal

A log of critical UX and accessibility learnings and best practices for the Google Agents CLI project.

## 2026-07-25 - [Cli Login Command Interactive By Default]
**Learning:** CLI setup or authentication flows should never force users to type extra flags like `--interactive` or `-i` when performing inherently interactive operations. Defaulting to interactive prompts on the first attempt reduces user friction, eliminates useless clicks/keystrokes, and creates an error-free first-time user authentication experience.
**Action:** Always design configuration, onboarding, or login CLI subcommands with a dual flag representation (such as click's `--interactive/--no-interactive`) defaulting to `True`, so programmatic or non-interactive use-cases can opt-out while human users get a seamless default experience.

## 2026-07-24 - [CLI Output Rich Styling & Readability]
**Learning:** Terminal CLI tools can feel dry and cognitively heavy when presenting configuration parameters in plain unstyled text. Introducing subtle color coding, typography weights, and structured visual groups (using tools like `rich`) dramatically improves visual scanning, screen reader focus clarity, and overall developer delight.
**Action:** Use structured labels with distinctive coloring (such as cyan for paths/names, green for active status, and yellow for alerts) to make key information instantly recognizable in standard output, while carefully retaining unchanged `--json` format outputs for reliable programmatic integrations.
