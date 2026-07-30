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

"""Tests for agents-cli login / auth commands."""

from unittest import mock
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


@mock.patch("google.agents.cli.setup.cmd_auth.run_auth_step")
@mock.patch("google.agents.cli.setup.cmd_auth.is_authenticated")
def test_login_defaults_to_interactive(mock_is_authenticated, mock_run_auth_step):
    """Verify that agents-cli login runs interactive auth by default."""
    runner = CliRunner()
    result = runner.invoke(cmd_login)

    assert result.exit_code == 0
    assert "Authentication" in result.output
    mock_run_auth_step.assert_called_once()


@mock.patch("google.agents.cli.setup.cmd_auth.run_auth_step")
@mock.patch("google.agents.cli.setup.cmd_auth.is_authenticated")
def test_login_status_not_authenticated(mock_is_authenticated, mock_run_auth_step):
    """Verify login --status when not authenticated."""
    mock_is_authenticated.return_value = (False, None)

    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--status"])

    assert result.exit_code == 0
    assert "Status" in result.output
    assert "Not authenticated" in result.output
    assert "Run 'agents-cli login' to authenticate." in result.output
    mock_run_auth_step.assert_not_called()


@mock.patch("google.agents.cli.setup.cmd_auth.run_auth_step")
@mock.patch("google.agents.cli.setup.cmd_auth.is_authenticated")
def test_login_status_authenticated(mock_is_authenticated, mock_run_auth_step):
    """Verify login --status when authenticated."""
    mock_is_authenticated.return_value = (True, "my-gcp-account@google.com")

    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--status"])

    assert result.exit_code == 0
    assert "Status" in result.output
    assert "Authenticated as my-gcp-account@google.com" in result.output
    mock_run_auth_step.assert_not_called()
