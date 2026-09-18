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

"""Tests for agents-cli install command."""

from unittest.mock import patch
from click.testing import CliRunner

from google.agents.cli.dev.cmd_install import cmd_install


def test_cmd_install_default():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_install.run") as mock_run:
        result = runner.invoke(cmd_install, [])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            ["uv", "sync"], check_err_msg="Failed to install dependencies"
        )
        assert "✓ Dependencies installed successfully." in result.output


def test_cmd_install_locked():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_install.run") as mock_run:
        result = runner.invoke(cmd_install, ["--locked"])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            ["uv", "sync", "--locked"], check_err_msg="Failed to install dependencies"
        )
        assert "✓ Dependencies installed successfully." in result.output


def test_cmd_install_clean(tmp_path):
    runner = CliRunner()
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\nversion = '0.1.0'\n")

    with (
        patch(
            "google.agents.cli.dev.cmd_install.find_project_root", return_value=tmp_path
        ),
        patch("google.agents.cli.dev.cmd_install.run") as mock_run,
    ):
        result = runner.invoke(cmd_install, ["--clean"])
        assert result.exit_code == 0
        assert not venv_dir.exists()
        assert "Cleaning virtual environment (.venv)..." in result.output
        assert "✓ Dependencies installed successfully." in result.output
        mock_run.assert_called_once_with(
            ["uv", "sync"], check_err_msg="Failed to install dependencies"
        )
