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

"""Tests for `agents-cli update` command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from google.agents.cli.setup.cmd_update import cmd_update


def test_cmd_update_cli_upgrade_failure():
    runner = CliRunner()
    mock_completed_process = MagicMock()
    mock_completed_process.returncode = 1

    with patch(
        "google.agents.cli.setup.cmd_update.run_npx_skills"
    ) as mock_npx_skills, patch(
        "google.agents.cli.setup._antigravity.link_skills_for_antigravity",
        return_value=[],
    ), patch(
        "google.agents.cli.setup.cmd_update.run",
        return_value=mock_completed_process,
    ) as mock_run:
        result = runner.invoke(cmd_update, ["-y"])

        assert result.exit_code == 0
        assert "✓ Skills updated." in result.output
        assert "CLI upgrade check skipped" in result.output
        mock_npx_skills.assert_called_once_with(["update", "-g"], "Updating skills")
        mock_run.assert_called_once_with(
            ["uv", "tool", "upgrade", "google-agents-cli"], check=False
        )


def test_cmd_update_cli_upgrade_success():
    runner = CliRunner()
    mock_completed_process = MagicMock()
    mock_completed_process.returncode = 0

    with patch(
        "google.agents.cli.setup.cmd_update.run_npx_skills"
    ) as mock_npx_skills, patch(
        "google.agents.cli.setup._antigravity.link_skills_for_antigravity",
        return_value=[],
    ), patch(
        "google.agents.cli.setup.cmd_update.run",
        return_value=mock_completed_process,
    ) as mock_run:
        result = runner.invoke(cmd_update, ["-y"])

        assert result.exit_code == 0
        assert "✓ Skills updated." in result.output
        assert "CLI upgrade check skipped" not in result.output
        mock_npx_skills.assert_called_once_with(["update", "-g"], "Updating skills")
        mock_run.assert_called_once_with(
            ["uv", "tool", "upgrade", "google-agents-cli"], check=False
        )
