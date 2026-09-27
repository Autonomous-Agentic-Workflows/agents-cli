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

"""Tests for agents-cli setup command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_setup import cmd_setup


def test_setup_interactive_by_default_when_unauthenticated():
    """Verify that 'setup' command runs interactive auth by default when unauthenticated."""
    runner = CliRunner()
    with (
        patch("google.agents.cli.auth.is_authenticated", return_value=(False, None)),
        patch("google.agents.cli.auth.run_auth_step") as mock_run_auth_step,
        patch("google.agents.cli.setup.cmd_setup.run") as mock_run,
        patch("google.agents.cli.setup.cmd_setup.run_npx_skills", return_value=["Installed"]),
        patch("google.agents.cli.setup._antigravity.link_skills_for_antigravity", return_value=[]),
    ):
        mock_run.return_value.stdout = "already installed"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0

        result = runner.invoke(cmd_setup, ["--dry-run"])
        assert result.exit_code == 0
        # In dry-run mode, it displays auth status
        assert "Auth:  Not authenticated" in result.output

    with (
        patch("google.agents.cli.auth.is_authenticated", return_value=(False, None)),
        patch("google.agents.cli.auth.run_auth_step") as mock_run_auth_step,
        patch("google.agents.cli.setup.cmd_setup.run") as mock_run,
        patch("google.agents.cli.setup.cmd_setup.run_npx_skills", return_value=["Installed"]),
        patch("google.agents.cli.setup._antigravity.link_skills_for_antigravity", return_value=[]),
    ):
        mock_run.return_value.stdout = "already installed"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0

        result = runner.invoke(cmd_setup)
        assert result.exit_code == 0
        mock_run_auth_step.assert_called_once_with(show_header=False)


def test_setup_no_interactive_when_unauthenticated():
    """Verify that 'setup --no-interactive' skips interactive auth prompt when unauthenticated."""
    runner = CliRunner()
    with (
        patch("google.agents.cli.auth.is_authenticated", return_value=(False, None)),
        patch("google.agents.cli.auth.run_auth_step") as mock_run_auth_step,
        patch("google.agents.cli.setup.cmd_setup.run") as mock_run,
        patch("google.agents.cli.setup.cmd_setup.run_npx_skills", return_value=["Installed"]),
        patch("google.agents.cli.setup._antigravity.link_skills_for_antigravity", return_value=[]),
    ):
        mock_run.return_value.stdout = "already installed"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0

        result = runner.invoke(cmd_setup, ["--no-interactive"])
        assert result.exit_code == 0
        mock_run_auth_step.assert_not_called()
        assert "Not authenticated" in result.output
        assert "Run without '--no-interactive' to authenticate interactively." in result.output
