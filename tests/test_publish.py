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

"""Tests for agents-cli publish gemini-enterprise command."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.publish.cmd_publish import register_gemini_enterprise


def test_publish_interactive_by_default():
    """Verify that 'publish gemini-enterprise' defaults to interactive mode."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.publish.cmd_publish.display_welcome_banner"
    ) as mock_welcome:
        # Prompting will happen or welcome banner will display because interactive=True
        result = runner.invoke(register_gemini_enterprise, input="1\nhttps://example.com/card.json\n")
        # In interactive mode with no metadata, it displays welcome banner
        mock_welcome.assert_called_once_with(register_mode=True)


def test_publish_no_interactive():
    """Verify that 'publish gemini-enterprise --no-interactive' disables interactive mode."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.publish.cmd_publish.display_welcome_banner"
    ) as mock_welcome:
        result = runner.invoke(register_gemini_enterprise, ["--no-interactive"])
        # Welcome banner should not be displayed in non-interactive mode
        mock_welcome.assert_not_called()
        assert result.exit_code != 0
        assert "--registration-type is required in programmatic mode" in result.output
