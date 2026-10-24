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

import click
from click.testing import CliRunner

from google.agents.cli._trust import require_confirmation


@click.command()
@require_confirmation("Are you sure you want to proceed?")
def dummy_command(yes, interactive):
    click.echo("Action executed.")


def test_require_confirmation_interactive_yes():
    runner = CliRunner()
    result = runner.invoke(dummy_command, ["--interactive"], input="y\n")
    assert result.exit_code == 0
    assert "Action executed." in result.output


def test_require_confirmation_interactive_no():
    runner = CliRunner()
    result = runner.invoke(dummy_command, ["--interactive"], input="n\n")
    assert result.exit_code == 0
    assert "Aborted." in result.output
    assert "Action executed." not in result.output


def test_require_confirmation_programmatic():
    runner = CliRunner()
    result = runner.invoke(dummy_command, [])
    assert result.exit_code == 0
    assert "Action executed." in result.output


def test_require_confirmation_bold_styled_prompt():
    runner = CliRunner()
    result = runner.invoke(dummy_command, ["--interactive"], input="y\n")
    assert result.exit_code == 0
    assert "Are you sure you want to proceed?" in result.output
