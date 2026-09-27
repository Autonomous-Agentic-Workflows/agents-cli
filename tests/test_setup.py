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

"""Tests for agents-cli setup command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.setup.cmd_setup import cmd_setup


def test_setup_dry_run():
    """Verify setup --dry-run prints command previews and dry run status without changes."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.auth.is_authenticated",
        return_value=(True, "user@example.com"),
    ):
        result = runner.invoke(cmd_setup, ["--dry-run"])
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        assert "Would install agents-cli:" in result.output
        assert "uv tool install google-agents-cli" in result.output
        assert "Would install skills:" in result.output
        assert "No changes made (dry run)." in result.output
        assert "  ▸ " in result.output
