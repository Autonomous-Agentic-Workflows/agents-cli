# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""agents-cli eval compare command — compare two eval result JSON files."""

import json
from pathlib import Path

import click

from google.agents.cli._output import emit


def _diff(base: dict, cand: dict, prefix: str = "") -> dict:
    """Compute a recursive diff between two eval result dicts.

    Nested dicts are diffed recursively with dotted key paths.
    Numeric changes include a delta (e.g., "+0.07" or "-0.03").
    """
    differences = {}

    all_keys = set(base.keys()) | set(cand.keys())
    for key in sorted(all_keys):
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        base_val = base.get(key)
        cand_val = cand.get(key)

        if base_val == cand_val:
            continue

        # Recurse into nested dicts
        if isinstance(base_val, dict) and isinstance(cand_val, dict):
            nested = _diff(base_val, cand_val, prefix=full_key)
            differences.update(nested["differences"])
            continue

        entry = {"baseline": base_val, "candidate": cand_val}
        if isinstance(base_val, (int, float)) and isinstance(cand_val, (int, float)):
            delta = cand_val - base_val
            if isinstance(delta, float):
                formatted_delta = f"+{delta:.4f}" if delta >= 0 else f"{delta:.4f}"
            else:
                formatted_delta = f"+{delta}" if delta >= 0 else str(delta)
            entry["delta"] = formatted_delta
        differences[full_key] = entry

    if prefix:
        return {"differences": differences}

    return {
        "baseline_keys": sorted(base.keys()),
        "candidate_keys": sorted(cand.keys()),
        "differences": differences,
        "changed_keys": sorted(differences.keys()),
        "unchanged_keys": sorted(k for k in all_keys if k not in differences),
    }


def _format_val(val) -> str:
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val) if val is not None else "(none)"


def _print_table(diff_result: dict, baseline_name: str, candidate_name: str) -> None:
    from rich.console import Console
    from rich.table import Table

    console = Console()
    differences = diff_result.get("differences", {})

    if not differences:
        console.print(
            "[yellow]No differences found between baseline and candidate.[/yellow]"
        )
        return

    table = Table(
        title=f"Evaluation Comparison: {baseline_name} vs {candidate_name}",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric / Key", style="cyan")
    table.add_column("Baseline", justify="right")
    table.add_column("Candidate", justify="right")
    table.add_column("Delta", justify="right")

    for key, entry in sorted(differences.items()):
        base_val = entry.get("baseline")
        cand_val = entry.get("candidate")
        base_str = _format_val(base_val)
        cand_str = _format_val(cand_val)

        if isinstance(base_val, (int, float)) and isinstance(cand_val, (int, float)):
            delta = cand_val - base_val
            if delta > 0:
                delta_str = (
                    f"[green]+{delta:.4f}[/green]"
                    if isinstance(delta, float)
                    else f"[green]+{delta}[/green]"
                )
            elif delta < 0:
                delta_str = (
                    f"[red]{delta:.4f}[/red]"
                    if isinstance(delta, float)
                    else f"[red]{delta}[/red]"
                )
            else:
                delta_str = f"[dim]{delta}[/dim]"
        else:
            delta_str = "[dim]N/A[/dim]"

        table.add_row(key, base_str, cand_str, delta_str)

    console.print(table)


@click.command("compare")
@click.argument("baseline", type=click.Path(exists=True))
@click.argument("candidate", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Output format (table or json).",
)
def cmd_compare(baseline, candidate, output_format):
    """Compare two eval result JSON files.

    Reads BASELINE and CANDIDATE JSON files and produces a diff.
    No subprocess calls — purely in-process comparison.
    """
    base_path = Path(baseline)
    cand_path = Path(candidate)
    base = json.loads(base_path.read_text(encoding="utf-8"))
    cand = json.loads(cand_path.read_text(encoding="utf-8"))
    diff_data = _diff(base, cand)

    if output_format.lower() == "json":
        emit(diff_data)
    else:
        _print_table(diff_data, base_path.name, cand_path.name)
