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

"""Tests for agents-cli upgrade command options."""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from google.agents.cli.scaffold.commands.upgrade import upgrade


def test_upgrade_interactive_by_default():
    """Verify that 'upgrade' command defaults to interactive=True."""
    runner = CliRunner()
    mock_config = MagicMock()
    mock_config.language = "python"
    mock_config.acli_version = "0.1.0"
    mock_config.project_name = "test-project"
    mock_config.agent_directory = "app"

    with (
        patch(
            "google.agents.cli.scaffold.commands.upgrade.find_project_root",
            return_value=None,
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.find_project_config",
            return_value=mock_config,
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.get_current_version",
            return_value="0.2.0",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade._ensure_uvx_available",
            return_value=True,
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.migrate_legacy_python_config",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.migrate_legacy_evalsets",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.warn_legacy_eval_config",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.run_three_way_merge",
            return_value=True,
        ) as mock_merge,
    ):
        result = runner.invoke(upgrade, [])
        assert result.exit_code == 0
        mock_merge.assert_called_once()
        assert mock_merge.call_args.kwargs["interactive"] is True


def test_upgrade_no_interactive():
    """Verify that 'upgrade --no-interactive' sets interactive=False."""
    runner = CliRunner()
    mock_config = MagicMock()
    mock_config.language = "python"
    mock_config.acli_version = "0.1.0"
    mock_config.project_name = "test-project"
    mock_config.agent_directory = "app"

    with (
        patch(
            "google.agents.cli.scaffold.commands.upgrade.find_project_root",
            return_value=None,
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.find_project_config",
            return_value=mock_config,
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.get_current_version",
            return_value="0.2.0",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade._ensure_uvx_available",
            return_value=True,
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.migrate_legacy_python_config",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.migrate_legacy_evalsets",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.warn_legacy_eval_config",
        ),
        patch(
            "google.agents.cli.scaffold.commands.upgrade.run_three_way_merge",
            return_value=True,
        ) as mock_merge,
    ):
        result = runner.invoke(upgrade, ["--no-interactive"])
        assert result.exit_code == 0
        mock_merge.assert_called_once()
        assert mock_merge.call_args.kwargs["interactive"] is False
