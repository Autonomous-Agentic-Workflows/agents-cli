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


def test_install_default():
    """Verify that 'install' command runs 'uv sync' and prints success message."""
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_install.run") as mock_run:
        result = runner.invoke(cmd_install)
        assert result.exit_code == 0
        mock_run.assert_called_once_with(["uv", "sync"], check_err_msg="Failed to install dependencies")
        assert "✓ Dependencies installed successfully." in result.output


def test_install_locked():
    """Verify that 'install --locked' passes '--locked' flag to 'uv sync'."""
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_install.run") as mock_run:
        result = runner.invoke(cmd_install, ["--locked"])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(["uv", "sync", "--locked"], check_err_msg="Failed to install dependencies")
        assert "✓ Dependencies installed successfully." in result.output


def test_install_clean(tmp_path):
    """Verify that 'install --clean' deletes .venv before running 'uv sync'."""
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "some_file.txt").write_text("test")

    runner = CliRunner()
    with (
        patch("google.agents.cli.dev.cmd_install.find_project_root", return_value=tmp_path),
        patch("google.agents.cli.dev.cmd_install.run") as mock_run,
    ):
        result = runner.invoke(cmd_install, ["--clean"])
        assert result.exit_code == 0
        assert not venv_dir.exists()
        mock_run.assert_called_once_with(["uv", "sync"], check_err_msg="Failed to install dependencies")
        assert "✓ Dependencies installed successfully." in result.output
