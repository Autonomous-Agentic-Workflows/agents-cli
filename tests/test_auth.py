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

"""Unit tests for the authentication login command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


def test_login_default_interactive():
    """Verify that 'login' runs interactively by default without needing -i."""
    runner = CliRunner()
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated", return_value=(False, None)) as mock_is_auth, \
         patch("google.agents.cli.setup.cmd_auth.run_auth_step") as mock_run_auth:

        result = runner.invoke(cmd_login)
        assert result.exit_code == 0
        mock_is_auth.assert_not_called()  # When running default login, it goes straight to run_auth_step (which checks internally)
        mock_run_auth.assert_called_once()
        assert "Authentication" in result.output


def test_login_no_interactive_error():
    """Verify that passing --no-interactive fails with a click.UsageError."""
    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--no-interactive"])
    assert result.exit_code != 0
    assert "requires interactive mode" in result.output
    assert "Do not pass --no-interactive" in result.output


def test_login_status_authenticated():
    """Verify status display when the user is already authenticated."""
    runner = CliRunner()
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated", return_value=(True, "test-user@google.com")):
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Authenticated as test-user@google.com" in result.output


def test_login_status_unauthenticated():
    """Verify status display when the user is not authenticated."""
    runner = CliRunner()
    with patch("google.agents.cli.setup.cmd_auth.is_authenticated", return_value=(False, None)):
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Status" in result.output
        assert "Not authenticated" in result.output
        assert "Run 'agents-cli login' to authenticate." in result.output
