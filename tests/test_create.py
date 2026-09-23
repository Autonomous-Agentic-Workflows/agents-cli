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

"""Tests for agents-cli create output formatting."""

from unittest.mock import patch
from click.testing import CliRunner
import click
from google.agents.cli.scaffold.commands.create import create


def test_create_output_formatting_new_dir():
    """Verify post-scaffold instructions when scaffolding into a new directory."""
    runner = CliRunner()
    mock_agents = {1: {"name": "adk", "language": "python", "description": "ADK Agent"}}
    with (
        patch(
            "google.agents.cli.scaffold.commands.create.template.get_available_agents",
            return_value=mock_agents,
        ),
        patch(
            "google.agents.cli.scaffold.commands.create.template.resolve_agent_alias",
            side_effect=lambda a: a,
        ),
        patch(
            "google.agents.cli.scaffold.commands.create.template.get_deployment_targets",
            return_value=["agent_runtime"],
        ),
        patch("google.agents.cli.scaffold.commands.create.template.get_template_path"),
        patch(
            "google.agents.cli.scaffold.commands.create.template.load_template_config",
            return_value={},
        ),
        patch("google.agents.cli.scaffold.commands.create.template.process_template"),
    ):
        result = runner.invoke(
            create,
            [
                "my-agent",
                "--agent",
                "adk",
                "--auto-approve",
                "--skip-checks",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "README:    cat my-agent/README.md" in result.output
        assert (
            "cd my-agent && agents-cli install && agents-cli playground"
            in result.output
        )


def test_create_output_formatting_in_folder():
    """Verify post-scaffold instructions when scaffolding in-folder (cd_path == '.')."""

    # We can test in_folder mode by invoking create via a dummy Click command that sets in_folder=True
    @click.command()
    @click.pass_context
    def dummy_cmd(ctx):
        ctx.invoke(
            create,
            project_name="my-agent",
            agent="adk",
            auto_approve=True,
            skip_checks=True,
            in_folder=True,
        )

    runner = CliRunner()
    mock_agents = {1: {"name": "adk", "language": "python", "description": "ADK Agent"}}
    with (
        patch(
            "google.agents.cli.scaffold.commands.create.template.get_available_agents",
            return_value=mock_agents,
        ),
        patch(
            "google.agents.cli.scaffold.commands.create.template.resolve_agent_alias",
            side_effect=lambda a: a,
        ),
        patch(
            "google.agents.cli.scaffold.commands.create.template.get_deployment_targets",
            return_value=["agent_runtime"],
        ),
        patch("google.agents.cli.scaffold.commands.create.template.get_template_path"),
        patch(
            "google.agents.cli.scaffold.commands.create.template.load_template_config",
            return_value={},
        ),
        patch("google.agents.cli.scaffold.commands.create.template.process_template"),
        patch("google.agents.cli.scaffold.utils.backup.create_project_backup"),
    ):
        result = runner.invoke(dummy_cmd)
        assert result.exit_code == 0, result.output
        assert "README:    cat README.md" in result.output
        assert "agents-cli install && agents-cli playground" in result.output
        assert "cd . &&" not in result.output
