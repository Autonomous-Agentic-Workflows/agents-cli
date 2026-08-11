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

"""Tests for the login / status CLI command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


def test_login_interactive_default_success():
    """Verify that by default, cmd_login runs the interactive authentication flow."""
    runner = CliRunner()
    with patch("google.agents.cli.setup.cmd_auth.run_auth_step") as mock_run_auth_step:
        result = runner.invoke(cmd_login)
        assert result.exit_code == 0
        mock_run_auth_step.assert_called_once()
        assert "Authentication" in result.output


def test_login_explicit_interactive_success():
    """Verify that cmd_login with explicit --interactive or -i runs the auth flow."""
    runner = CliRunner()
    for flag in ["--interactive", "-i"]:
        with patch(
            "google.agents.cli.setup.cmd_auth.run_auth_step"
        ) as mock_run_auth_step:
            result = runner.invoke(cmd_login, [flag])
            assert result.exit_code == 0
            mock_run_auth_step.assert_called_once()
            assert "Authentication" in result.output


def test_login_no_interactive_error():
    """Verify that passing --no-interactive raises a Click usage error."""
    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--no-interactive"])
    assert result.exit_code != 0
    assert "requires interactive mode" in result.output


def test_login_status_authenticated():
    """Verify status output when the user is authenticated."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(True, "test-user@google.com (ADC)"),
    ) as mock_is_authenticated:
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        mock_is_authenticated.assert_called_once()
        assert "Status" in result.output
        assert "Authenticated as test-user@google.com (ADC)" in result.output


def test_login_status_not_authenticated():
    """Verify status output when the user is not authenticated."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(False, None),
    ) as mock_is_authenticated:
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        mock_is_authenticated.assert_called_once()
        assert "Status" in result.output
        assert "Not authenticated" in result.output
        assert "Run 'agents-cli login' to authenticate" in result.output
