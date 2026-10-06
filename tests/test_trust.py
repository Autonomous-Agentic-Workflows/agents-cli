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

"""Tests for trust tier decorators."""

from unittest.mock import patch

import click
from click.testing import CliRunner

from google.agents.cli._trust import require_confirmation


@click.command()
@require_confirmation("Are you sure you want to proceed?")
def dummy_cmd(yes: bool, interactive: bool):
    click.echo("Execution completed.")


def test_require_confirmation_interactive_yes():
    runner = CliRunner()
    with patch("click.confirm", return_value=True) as mock_confirm:
        result = runner.invoke(dummy_cmd, ["--interactive"])
        assert result.exit_code == 0
        assert "Execution completed." in result.output
        mock_confirm.assert_called_once()
        formatted_prompt = mock_confirm.call_args[0][0]
        assert "Are you sure you want to proceed?" in formatted_prompt


def test_require_confirmation_interactive_no():
    runner = CliRunner()
    with patch("click.confirm", return_value=False) as mock_confirm:
        result = runner.invoke(dummy_cmd, ["--interactive"])
        assert result.exit_code == 0
        assert "Aborted." in result.output
        assert "Execution completed." not in result.output
        mock_confirm.assert_called_once()


def test_require_confirmation_auto_approve():
    runner = CliRunner()
    with patch("click.confirm") as mock_confirm:
        result = runner.invoke(dummy_cmd, ["--yes"])
        assert result.exit_code == 0
        assert "Execution completed." in result.output
        mock_confirm.assert_not_called()


def test_require_confirmation_programmatic_default():
    runner = CliRunner()
    with patch("click.confirm") as mock_confirm:
        result = runner.invoke(dummy_cmd, [])
        assert result.exit_code == 0
        assert "Execution completed." in result.output
        mock_confirm.assert_not_called()
