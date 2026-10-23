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

import click
from click.testing import CliRunner

from google.agents.cli._trust import require_confirmation


def test_require_confirmation_interactive_yes():
    @click.command()
    @require_confirmation("Are you sure?")
    def dummy_cmd(yes, interactive):
        click.echo("Executed!")

    runner = CliRunner()
    result = runner.invoke(dummy_cmd, ["--interactive"], input="y\n")
    assert result.exit_code == 0
    assert "Are you sure?" in result.output
    assert "Executed!" in result.output


def test_require_confirmation_interactive_no():
    @click.command()
    @require_confirmation("Are you sure?")
    def dummy_cmd(yes, interactive):
        click.echo("Executed!")

    runner = CliRunner()
    result = runner.invoke(dummy_cmd, ["--interactive"], input="n\n")
    assert result.exit_code == 0
    assert "Are you sure?" in result.output
    assert "Aborted." in result.output
    assert "Executed!" not in result.output


def test_require_confirmation_yes_flag():
    @click.command()
    @require_confirmation("Are you sure?")
    def dummy_cmd(yes, interactive):
        click.echo("Executed!")

    runner = CliRunner()
    result = runner.invoke(dummy_cmd, ["--yes"])
    assert result.exit_code == 0
    assert "Executed!" in result.output
