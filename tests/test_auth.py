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

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_auth import cmd_login


def test_cmd_login_status_authenticated():
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(True, "Fake Auth Display"),
    ):
        runner = CliRunner()
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Authenticated as Fake Auth Display" in result.output


def test_cmd_login_status_not_authenticated():
    with patch(
        "google.agents.cli.setup.cmd_auth.is_authenticated",
        return_value=(False, None),
    ):
        runner = CliRunner()
        result = runner.invoke(cmd_login, ["--status"])
        assert result.exit_code == 0
        assert "Not authenticated" in result.output
        assert "Run 'agents-cli login' to authenticate." in result.output


def test_cmd_login_default_interactive():
    with patch("google.agents.cli.setup.cmd_auth.run_auth_step") as mock_run_auth_step:
        runner = CliRunner()
        result = runner.invoke(cmd_login)
        assert result.exit_code == 0
        assert "Authentication" in result.output
        mock_run_auth_step.assert_called_once()


def test_cmd_login_no_interactive():
    runner = CliRunner()
    result = runner.invoke(cmd_login, ["--no-interactive"])
    assert result.exit_code != 0
    assert "requires interactive mode" in result.output
