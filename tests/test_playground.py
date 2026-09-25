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

"""Tests for agents-cli playground command."""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from google.agents.cli.dev.cmd_playground import cmd_playground


def test_playground_default_no_open():
    """Verify that playground command runs without opening browser by default."""
    runner = CliRunner()
    mock_cfg = MagicMock()
    mock_cfg.agent_directory = "my_agent"

    with (
        patch("google.agents.cli.dev.cmd_playground.chdir_project_root"),
        patch(
            "google.agents.cli.dev.cmd_playground.read_project_config",
            return_value=mock_cfg,
        ),
        patch("google.agents.cli.dev.cmd_playground.require_agent_directory"),
        patch("google.agents.cli.dev.cmd_playground.run") as mock_run,
        patch("webbrowser.open") as mock_webbrowser_open,
    ):
        result = runner.invoke(cmd_playground)
        assert result.exit_code == 0
        mock_run.assert_called_once()
        mock_webbrowser_open.assert_not_called()


def test_playground_open_flag():
    """Verify that playground --open opens the browser with the playground URL."""
    runner = CliRunner()
    mock_cfg = MagicMock()
    mock_cfg.agent_directory = "my_agent"

    with (
        patch("google.agents.cli.dev.cmd_playground.chdir_project_root"),
        patch(
            "google.agents.cli.dev.cmd_playground.read_project_config",
            return_value=mock_cfg,
        ),
        patch("google.agents.cli.dev.cmd_playground.require_agent_directory"),
        patch("google.agents.cli.dev.cmd_playground.run") as mock_run,
        patch("webbrowser.open") as mock_webbrowser_open,
    ):
        result = runner.invoke(cmd_playground, ["--open"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        mock_webbrowser_open.assert_called_once_with(
            "http://127.0.0.1:8080/dev-ui/?app=my_agent"
        )


def test_playground_short_open_flag():
    """Verify that playground -o opens the browser with the playground URL."""
    runner = CliRunner()
    mock_cfg = MagicMock()
    mock_cfg.agent_directory = "my_agent"

    with (
        patch("google.agents.cli.dev.cmd_playground.chdir_project_root"),
        patch(
            "google.agents.cli.dev.cmd_playground.read_project_config",
            return_value=mock_cfg,
        ),
        patch("google.agents.cli.dev.cmd_playground.require_agent_directory"),
        patch("google.agents.cli.dev.cmd_playground.run") as mock_run,
        patch("webbrowser.open") as mock_webbrowser_open,
    ):
        result = runner.invoke(cmd_playground, ["-o"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        mock_webbrowser_open.assert_called_once_with(
            "http://127.0.0.1:8080/dev-ui/?app=my_agent"
        )
