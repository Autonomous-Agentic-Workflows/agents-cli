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

"""Show project configuration, paths, and CLI version."""

from __future__ import annotations

import platform
from pathlib import Path

import click
from rich.console import Console

import google.agents.cli as _cli_pkg
from google.agents.cli.__init__ import __version__
from google.agents.cli._output import emit
from google.agents.cli._project import (
    check_cli_version,
    find_project_root,
    read_project_config,
)
from google.agents.cli._skills_check import get_installed_skills

_CLI_INSTALL_PATH = str(Path(_cli_pkg.__file__).parent)
console = Console()


def _print_installed_skills(
    skills: list[dict] | None,
) -> None:
    """Print installed skills summary with rich color formatting."""
    if skills is None:
        console.print("Installed skills:   [bold red](could not query)[/bold red]")
        return
    if not skills:
        console.print("Installed skills:   [bold yellow]none[/bold yellow]")
        return
    # Group by scope
    by_scope: dict[str, list[str]] = {}
    for s in skills:
        scope = s.get("scope", "unknown")
        by_scope.setdefault(scope, []).append(s["name"])
    for scope, names in sorted(by_scope.items()):
        console.print(
            f"Installed skills:   [bold green]{len(names)}[/bold green] [dim]({scope})[/dim]"
        )
        for name in sorted(names):
            console.print(f"  [cyan]•[/cyan] [bold]{name}[/bold]")


@click.command()
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def cmd_info(as_json: bool) -> None:
    """Show project configuration, paths, and CLI version."""
    installed_skills = get_installed_skills()
    project_root = find_project_root()
    os_info = platform.platform()
    if project_root is None:
        if as_json:
            emit(
                {
                    "cli_version": __version__,
                    "cli_install_path": _CLI_INSTALL_PATH,
                    "os_info": os_info,
                    "installed_skills": installed_skills,
                    "project": None,
                }
            )
        else:
            console.print(f"CLI version:        [bold green]{__version__}[/bold green]")
            console.print(f"CLI install path:   [cyan]{_CLI_INSTALL_PATH}[/cyan]")
            console.print(f"OS info:            [dim]{os_info}[/dim]")
            _print_installed_skills(installed_skills)
            console.print()
            console.print(
                "[bold yellow]No agent project found in the current directory or any parent.[/bold yellow]"
            )
            console.print("  Run this command from within a project, or create one:")
            console.print("    [bold cyan]agents-cli create my-agent[/bold cyan]")
        return

    cfg = read_project_config(str(project_root))
    check_cli_version(cfg)

    info = {
        "cli_version": __version__,
        "cli_install_path": _CLI_INSTALL_PATH,
        "os_info": os_info,
        "installed_skills": installed_skills,
        "project_root": str(project_root),
        "project_name": cfg.project_name,
        "deployment_target": cfg.deployment_target,
        "agent_directory": cfg.agent_directory,
        "is_a2a": cfg.is_a2a,
        "region": cfg.region,
    }

    if as_json:
        emit(info)
        return

    console.print(f"CLI version:        [bold green]{__version__}[/bold green]")
    console.print(f"CLI install path:   [cyan]{_CLI_INSTALL_PATH}[/cyan]")
    console.print(f"OS info:            [dim]{os_info}[/dim]")
    _print_installed_skills(installed_skills)
    console.print()
    console.print(f"Project root:       [cyan]{project_root}[/cyan]")
    console.print(
        f"Project name:       [bold green]{cfg.project_name or '(not set)'}[/bold green]"
    )
    console.print(f"Deployment target:  [bold cyan]{cfg.deployment_target}[/bold cyan]")
    console.print(f"Agent directory:    [cyan]{cfg.agent_directory}[/cyan]")
    console.print(f"Region:             [cyan]{cfg.region}[/cyan]")
    if cfg.is_a2a:
        console.print("A2A:                [bold green]yes[/bold green]")
