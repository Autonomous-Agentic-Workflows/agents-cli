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

"""Unit tests for trust tier decorators."""

import click
from click.testing import CliRunner
from google.agents.cli._trust import require_confirmation


@click.command()
@require_confirmation("Are you sure you want to delete this resource?")
def dummy_cmd(yes: bool, interactive: bool):
    click.echo("Executed command successfully.")


def test_require_confirmation_interactive_accept():
    runner = CliRunner()
    result = runner.invoke(dummy_cmd, ["-i"], input="y\n")
    assert result.exit_code == 0
    assert "Executed command successfully." in result.output


def test_require_confirmation_interactive_abort():
    runner = CliRunner()
    result = runner.invoke(dummy_cmd, ["-i"], input="n\n")
    assert result.exit_code == 0
    assert "Aborted." in result.output
    assert "Executed command successfully." not in result.output


def test_require_confirmation_yes_flag():
    runner = CliRunner()
    result = runner.invoke(dummy_cmd, ["-y"])
    assert result.exit_code == 0
    assert "Executed command successfully." in result.output


def test_require_confirmation_default_programmatic():
    runner = CliRunner()
    result = runner.invoke(dummy_cmd, [])
    assert result.exit_code == 0
    assert "Executed command successfully." in result.output
