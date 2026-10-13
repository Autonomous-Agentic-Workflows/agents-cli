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

"""Tests for agents-cli merge utilities and upgrade command options."""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from google.agents.cli.scaffold.commands.upgrade import upgrade
from google.agents.cli.scaffold.utils.merge import display_results
from google.agents.cli.scaffold.utils.upgrade import FileCompareResult


def test_upgrade_passes_interactive_flag():
    """Verify that 'upgrade' passes interactive=False by default and interactive=True with -i."""
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
        assert mock_merge.call_args.kwargs["interactive"] is False

        result_interactive = runner.invoke(upgrade, ["-i"])
        assert result_interactive.exit_code == 0
        assert mock_merge.call_args.kwargs["interactive"] is True


def test_display_results_conflict_guidance(capsys):
    """Verify display_results outputs accurate conflict guidance for interactive and non-interactive modes."""
    conflict_item = FileCompareResult(
        path="app/agent.py",
        action="conflict",
        reason="both_changed",
        category="agent_code",
    )
    groups = {
        "auto_update": [],
        "preserve": [],
        "skip": [],
        "new": [],
        "removed": [],
        "conflict": [conflict_item],
    }

    # Non-interactive mode (default)
    display_results(groups, interactive=False)
    captured_non_interactive = capsys.readouterr().out
    assert "Keeping your version for conflicts" in captured_non_interactive
    assert "--interactive (-i)" in captured_non_interactive

    # Interactive mode
    display_results(groups, interactive=True)
    captured_interactive = capsys.readouterr().out
    assert "You'll be prompted to resolve each conflict" in captured_interactive
