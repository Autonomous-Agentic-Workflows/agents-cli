## 2026-03-04 - [Consistent Success Indicators Across Subcommands]
**Learning:** Terminal CLI output feels disjointed when different subcommands use varying formats for completed actions (e.g., plain text vs. styled strings vs. unformatted paths). Standardizing saved artifact and completion messages with a prominent `[bold green]✓ ... saved to:[/bold green]` prefix establishes visual hierarchy and instant status recognition across terminal themes.
**Action:** Use `[bold green]✓ ...[/bold green]` for success indicators in CLI output consistently across all subcommand groups.

## 2026-03-04 - [Defaulting CLI Commands to Interactive Mode]
**Learning:** In CLI applications, forcing users to explicitly pass flags (like `--interactive` or `-i`) to initiate standard command flows is a common friction point and a bad user experience. When a user runs a command whose purpose is interactive (like `login` or `setup`), the command should default to interactive mode unless run in a scripting/non-interactive context. The option to disable interactive behavior should still be provided via flags (like `--no-interactive`), but should not be the hurdle to getting started.
**Action:** Always design user-centric CLI workflows to be interactive by default, using `--no-interactive` flags to override default behavior rather than requiring `--interactive` or `-i` to proceed.
