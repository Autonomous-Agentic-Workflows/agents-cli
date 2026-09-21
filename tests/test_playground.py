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

"""Unit tests for agents-cli playground command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from google.agents.cli._project import ProjectConfig
from google.agents.cli.dev.cmd_playground import cmd_playground


@patch("google.agents.cli.dev.cmd_playground.run")
@patch("google.agents.cli.dev.cmd_playground.require_agent_directory")
@patch("google.agents.cli.dev.cmd_playground.read_project_config")
@patch("google.agents.cli.dev.cmd_playground.chdir_project_root")
@patch("webbrowser.open")
def test_cmd_playground_open_browser_flag(
    mock_webbrowser_open,
    mock_chdir,
    mock_read_config,
    mock_require_dir,
    mock_run,
):
    mock_config = MagicMock(spec=ProjectConfig)
    mock_config.agent_directory = "my_agent"
    mock_read_config.return_value = mock_config

    runner = CliRunner()

    # Test without --open flag
    result = runner.invoke(cmd_playground, [])
    assert result.exit_code == 0
    mock_webbrowser_open.assert_not_called()

    # Test with --open flag
    result_open = runner.invoke(cmd_playground, ["--open"])
    assert result_open.exit_code == 0
    mock_webbrowser_open.assert_called_once_with(
        "http://127.0.0.1:8080/dev-ui/?app=my_agent"
    )

    mock_webbrowser_open.reset_mock()

    # Test with -o short flag
    result_o = runner.invoke(cmd_playground, ["-o"])
    assert result_o.exit_code == 0
    mock_webbrowser_open.assert_called_once_with(
        "http://127.0.0.1:8080/dev-ui/?app=my_agent"
    )
