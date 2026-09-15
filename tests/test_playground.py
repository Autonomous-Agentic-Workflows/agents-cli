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

from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli._project import ProjectConfig
from google.agents.cli.dev.cmd_playground import cmd_playground


@patch("google.agents.cli.dev.cmd_playground.run")
@patch("google.agents.cli.dev.cmd_playground.require_agent_directory")
@patch("google.agents.cli.dev.cmd_playground.read_project_config")
@patch("google.agents.cli.dev.cmd_playground.chdir_project_root")
def test_playground_default(
    mock_chdir, mock_read_config, mock_require, mock_run
):
    mock_read_config.return_value = ProjectConfig(agent_directory="my_agent")
    runner = CliRunner()

    result = runner.invoke(cmd_playground, [])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "adk" in args
    assert "web" in args


@patch("webbrowser.open")
@patch("google.agents.cli.dev.cmd_playground.run")
@patch("google.agents.cli.dev.cmd_playground.require_agent_directory")
@patch("google.agents.cli.dev.cmd_playground.read_project_config")
@patch("google.agents.cli.dev.cmd_playground.chdir_project_root")
def test_playground_open_flag(
    mock_chdir, mock_read_config, mock_require, mock_run, mock_webbrowser_open
):
    mock_read_config.return_value = ProjectConfig(agent_directory="my_agent")
    runner = CliRunner()

    result = runner.invoke(cmd_playground, ["--open"])

    assert result.exit_code == 0
    mock_webbrowser_open.assert_called_once_with(
        "http://127.0.0.1:8080/dev-ui/?app=my_agent"
    )


@patch("webbrowser.open")
@patch("google.agents.cli.dev.cmd_playground.run")
@patch("google.agents.cli.dev.cmd_playground.require_agent_directory")
@patch("google.agents.cli.dev.cmd_playground.read_project_config")
@patch("google.agents.cli.dev.cmd_playground.chdir_project_root")
def test_playground_open_short_flag(
    mock_chdir, mock_read_config, mock_require, mock_run, mock_webbrowser_open
):
    mock_read_config.return_value = ProjectConfig(agent_directory="my_agent")
    runner = CliRunner()

    result = runner.invoke(cmd_playground, ["-o"])

    assert result.exit_code == 0
    mock_webbrowser_open.assert_called_once_with(
        "http://127.0.0.1:8080/dev-ui/?app=my_agent"
    )
