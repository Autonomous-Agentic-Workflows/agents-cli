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

"""Unit tests for agents-cli dev commands (cmd_lint and cmd_install)."""

from unittest.mock import patch
from click.testing import CliRunner

from google.agents.cli.dev.cmd_install import cmd_install
from google.agents.cli.dev.cmd_lint import cmd_lint


def test_cmd_lint_success_message():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_lint.run") as mock_run:
        result = runner.invoke(cmd_lint, [])
        assert result.exit_code == 0
        assert "✓ All code quality checks passed!" in result.output
        assert mock_run.called


def test_cmd_lint_fix_success_message():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_lint.run") as mock_run:
        result = runner.invoke(cmd_lint, ["--fix"])
        assert result.exit_code == 0
        assert "✓ Code formatting and linting completed." in result.output
        assert mock_run.called


def test_cmd_install_success_message():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_install.run") as mock_run:
        result = runner.invoke(cmd_install, [])
        assert result.exit_code == 0
        assert "✓ Dependencies installed successfully." in result.output
        assert mock_run.called


def test_cmd_install_clean_message(tmp_path):
    runner = CliRunner()
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\n")

    with patch("google.agents.cli.dev.cmd_install.run") as mock_run, patch(
        "google.agents.cli.dev.cmd_install.find_project_root", return_value=tmp_path
    ):
        result = runner.invoke(cmd_install, ["--clean"])
        assert result.exit_code == 0
        assert "✓ Cleaned existing virtual environment (.venv)." in result.output
        assert "✓ Dependencies installed successfully." in result.output
        assert not venv_dir.exists()
        assert mock_run.called
