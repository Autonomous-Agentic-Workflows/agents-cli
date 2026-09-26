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

"""Tests for trust tier confirmation decorators."""

import click
from click.testing import CliRunner

from google.agents.cli._trust import require_confirmation


@click.command()
@require_confirmation("Are you sure you want to proceed?")
def sample_cmd(yes, interactive):
    click.echo("Executed command")


def test_require_confirmation_interactive_yes():
    runner = CliRunner()
    result = runner.invoke(sample_cmd, ["--interactive"], input="y\n")
    assert result.exit_code == 0
    assert "Are you sure you want to proceed?" in result.output
    assert "Executed command" in result.output


def test_require_confirmation_interactive_no():
    runner = CliRunner()
    result = runner.invoke(sample_cmd, ["--interactive"], input="n\n")
    assert result.exit_code == 0
    assert "Are you sure you want to proceed?" in result.output
    assert "Aborted." in result.output
    assert "Executed command" not in result.output


def test_require_confirmation_auto_approve():
    runner = CliRunner()
    result = runner.invoke(sample_cmd, ["--yes"])
    assert result.exit_code == 0
    assert "Are you sure you want to proceed?" not in result.output
    assert "Executed command" in result.output


def test_require_confirmation_strict_mode():
    runner = CliRunner()
    result = runner.invoke(sample_cmd, [])
    assert result.exit_code == 0
    assert "Are you sure you want to proceed?" not in result.output
    assert "Executed command" in result.output
