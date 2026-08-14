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

"""Tests for agents-cli login / status command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


def test_login_interactive_defaults_authenticated():
    """Test that login command defaults to interactive, and shows authenticated status when already authenticated."""
    with patch("google.agents.cli.auth.is_authenticated") as mock_auth_is_authed, \
         patch("google.agents.cli.setup.cmd_auth.is_authenticated") as mock_setup_is_authed:
        mock_auth_is_authed.return_value = (True, "Mocked User (mock@google.com)")
        mock_setup_is_authed.return_value = (True, "Mocked User (mock@google.com)")

        runner = CliRunner()
        result = runner.invoke(cmd_login, [])

        assert result.exit_code == 0
        assert "Authenticated as Mocked User (mock@google.com)" in result.output


def test_login_interactive_defaults_unauthenticated():
    """Test that login command defaults to interactive, and triggers auth step when not authenticated."""
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated") as mock_is_authenticated, \
         patch("google.agents.cli.setup.cmd_auth.run_auth_step") as mock_run_auth_step:
        mock_is_authenticated.return_value = (False, None)

        runner = CliRunner()
        result = runner.invoke(cmd_login, [])

        assert result.exit_code == 0
        assert "Authentication" in result.output
        mock_run_auth_step.assert_called_once()


def test_login_status_unauthenticated():
    """Test that login --status shows correct messages when unauthenticated."""
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated") as mock_is_authenticated:
        mock_is_authenticated.return_value = (False, None)

        runner = CliRunner()
        result = runner.invoke(cmd_login, ["--status"])

        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Authentication" in result.output
        assert "Not authenticated" in result.output
        assert "Run 'agents-cli login' to authenticate." in result.output


def test_login_status_authenticated():
    """Test that login --status shows correct messages when authenticated."""
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated") as mock_is_authenticated:
        mock_is_authenticated.return_value = (True, "Mocked User (mock@google.com)")

        runner = CliRunner()
        result = runner.invoke(cmd_login, ["--status"])

        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Authentication" in result.output
        assert "Authenticated as Mocked User (mock@google.com)" in result.output


def test_login_non_interactive_error_when_unauthenticated():
    """Test that login --non-interactive fails with UsageError when unauthenticated."""
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated") as mock_is_authenticated:
        mock_is_authenticated.return_value = (False, None)

        runner = CliRunner()
        result = runner.invoke(cmd_login, ["--non-interactive"])

        assert result.exit_code != 0
        assert "requires interactive mode" in result.output
