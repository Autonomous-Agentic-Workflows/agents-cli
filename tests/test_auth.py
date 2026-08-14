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

"""Tests for the login command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


def test_login_interactive_by_default():
    """Verify that 'login' command runs in interactive mode by default (without -i)."""
    runner = CliRunner()
    # Mock is_authenticated to return False so that it attempts to run auth step
    with (
        patch(
            "google.agents.cli.setup.cmd_auth.is_authenticated",
            return_value=(False, None),
        ),
        patch("google.agents.cli.setup.cmd_auth.run_auth_step") as mock_run_auth_step,
    ):
        result = runner.invoke(cmd_login)
        assert result.exit_code == 0
        assert "Authentication" in result.output
        mock_run_auth_step.assert_called_once()


def test_login_non_interactive_raises_error():
    """Verify that '--non-interactive' raises a UsageError."""
    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--non-interactive"])
    assert result.exit_code != 0
    assert "requires interactive mode" in result.output


def test_login_status_authenticated():
    """Verify '--status' when authenticated."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(True, "Mock User"),
    ):
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Authenticated as Mock User" in result.output


def test_login_status_unauthenticated():
    """Verify '--status' when not authenticated."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated", return_value=(False, None)
    ):
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Not authenticated" in result.output
        assert "Run 'agents-cli login' to authenticate" in result.output
