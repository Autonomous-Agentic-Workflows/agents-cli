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


@patch("google.agents.cli.dev.cmd_playground.run")
@patch("google.agents.cli.dev.cmd_playground.require_agent_directory")
@patch("google.agents.cli.dev.cmd_playground.read_project_config")
@patch("google.agents.cli.dev.cmd_playground.chdir_project_root")
def test_cmd_playground_default(
    mock_chdir, mock_read_cfg, mock_req_agent_dir, mock_run
):
    cfg = MagicMock()
    cfg.agent_directory = "my_agent"
    mock_read_cfg.return_value = cfg

    runner = CliRunner()
    result = runner.invoke(cmd_playground, [])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0][:4] == ["uv", "run", "adk", "web"]


@patch("webbrowser.open")
@patch("google.agents.cli.dev.cmd_playground.run")
@patch("google.agents.cli.dev.cmd_playground.require_agent_directory")
@patch("google.agents.cli.dev.cmd_playground.read_project_config")
@patch("google.agents.cli.dev.cmd_playground.chdir_project_root")
def test_cmd_playground_open_browser(
    mock_chdir, mock_read_cfg, mock_req_agent_dir, mock_run, mock_webbrowser_open
):
    cfg = MagicMock()
    cfg.agent_directory = "my_agent"
    mock_read_cfg.return_value = cfg

    runner = CliRunner()
    result = runner.invoke(cmd_playground, ["--open", "--port", "9090"])

    assert result.exit_code == 0
    mock_webbrowser_open.assert_called_once_with(
        "http://127.0.0.1:9090/dev-ui/?app=my_agent"
    )
    mock_run.assert_called_once()
