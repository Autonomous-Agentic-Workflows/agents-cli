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

"""Unit tests for the agents-cli login/status command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


def test_login_default_interactive_mode():
    """Verify that running 'agents-cli login' triggers interactive authentication by default."""
    runner = CliRunner()
    with patch("google.agents.cli.setup.cmd_auth.run_auth_step") as mock_run_auth_step:
        result = runner.invoke(cmd_login)
        assert result.exit_code == 0
        mock_run_auth_step.assert_called_once()
        assert "Authentication" in result.output


def test_login_no_interactive_raises_usage_error():
    """Verify that '--no-interactive' raises an error since login requires interaction."""
    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--no-interactive"])
    assert result.exit_code != 0
    assert "'login' requires interactive mode" in result.output


def test_login_status_authenticated():
    """Verify '--status' displays the correct email when authenticated."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(True, "test-user@google.com"),
    ):
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Authenticated as test-user@google.com" in result.output


def test_login_status_not_authenticated():
    """Verify '--status' displays help message when not authenticated."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(False, None),
    ):
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Not authenticated" in result.output
        assert "Run 'agents-cli login' to authenticate." in result.output
