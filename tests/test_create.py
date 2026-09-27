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

"""Tests for agents-cli create / scaffold create command interactive defaults."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.scaffold.commands.create import create


def test_create_defaults_to_interactive_when_no_project_name():
    """Verify that 'create' defaults to interactive prompt when project_name is omitted."""
    runner = CliRunner()
    # Prompting for project name when interactive=True
    with patch("rich.prompt.Prompt.ask", return_value="my-test-agent") as mock_prompt_ask:
        with patch("google.agents.cli.scaffold.commands.create.display_agent_selection") as mock_select:
            # Abort inside selection flow or return dummy
            mock_select.side_effect = Exception("Stop execution after selection call")
            result = runner.invoke(create)
            mock_prompt_ask.assert_called()
            assert "Enter a name for your project" in mock_prompt_ask.call_args[0][0]


def test_create_no_interactive_without_project_name_raises_usage_error():
    """Verify that 'create --no-interactive' without project_name raises UsageError."""
    runner = CliRunner()
    result = runner.invoke(create, ["--no-interactive"])
    assert result.exit_code != 0
    assert "project-name is a required argument in programmatic mode" in result.output


def test_create_auto_approve_without_project_name_uses_default():
    """Verify that 'create --auto-approve --no-interactive' uses default project name 'my-agent' without prompting."""
    runner = CliRunner()
    with patch("rich.prompt.Prompt.ask") as mock_prompt_ask:
        with patch("google.agents.cli.scaffold.utils.template.process_template"):
            with patch("google.agents.cli.scaffold.commands.create._setup_gcp_environment", return_value={"project": "test-proj"}):
                result = runner.invoke(create, ["--auto-approve", "--no-interactive", "--skip-checks"])
                mock_prompt_ask.assert_not_called()
                assert "Defaulting to 'my-agent' in auto-approve mode." in result.output
