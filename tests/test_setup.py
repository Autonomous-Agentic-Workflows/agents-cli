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
    """Verify setup command defaults to interactive authentication when unauthenticated."""
    runner = CliRunner()
    with (
        patch("google.agents.cli.auth.is_authenticated", return_value=(False, None)),
        patch("google.agents.cli.auth.run_auth_step") as mock_run_auth_step,
        patch("google.agents.cli.setup.cmd_setup.run") as mock_run,
        patch("google.agents.cli.setup.cmd_setup.run_npx_skills") as mock_skills,
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Installed"
        mock_run.return_value.stderr = ""
        mock_skills.return_value = ["Installed"]

        result = runner.invoke(cmd_setup)
        assert result.exit_code == 0
        mock_run_auth_step.assert_called_once_with(show_header=False)


def test_setup_no_interactive_skips_auth_step():
    """Verify setup command with --no-interactive skips run_auth_step when unauthenticated."""
    runner = CliRunner()
    with (
        patch("google.agents.cli.auth.is_authenticated", return_value=(False, None)),
        patch("google.agents.cli.auth.run_auth_step") as mock_run_auth_step,
        patch("google.agents.cli.setup.cmd_setup.run") as mock_run,
        patch("google.agents.cli.setup.cmd_setup.run_npx_skills") as mock_skills,
    ):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Installed"
        mock_run.return_value.stderr = ""
        mock_skills.return_value = ["Installed"]

        result = runner.invoke(cmd_setup, ["--no-interactive"])
        assert result.exit_code == 0
        mock_run_auth_step.assert_not_called()
        assert "Not authenticated. Run 'agents-cli login' to authenticate." in result.output
