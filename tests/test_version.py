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

"""Unit tests for the non-blocking version update check system."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from google.agents.cli.scaffold.utils import version


@pytest.fixture
def temp_paths(tmp_path):
    """Fixture to mock stamp and cache paths to point to tmp_path."""
    stamp = tmp_path / ".acli_update_check"
    cache = tmp_path / ".acli_latest_version"
    with (
        patch("google.agents.cli.scaffold.utils.version._UPDATE_CHECK_STAMP", stamp),
        patch("google.agents.cli.scaffold.utils.version._LATEST_VERSION_CACHE", cache),
    ):
        yield stamp, cache


def test_update_check_not_due_no_new_version(temp_paths):
    """Test that if update check is not due and no newer version is in cache, nothing happens."""
    stamp, cache = temp_paths
    stamp.write_text(str(version.time.time()))  # Just ran, so not due

    with (
        patch(
            "google.agents.cli.scaffold.utils.version.get_current_version",
            return_value="1.0.0",
        ),
        patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen,
        patch("rich.console.Console") as mock_console_class,
    ):
        version.display_update_message()

        # No background process spawned
        mock_popen.assert_not_called()
        # No message printed
        mock_console_class.assert_not_called()


def test_update_check_not_due_but_update_available(temp_paths):
    """Test that if update check is not due but cache has a newer version, the message is displayed but no background process is spawned."""
    stamp, cache = temp_paths
    stamp.write_text(str(version.time.time()))  # Just ran, so not due
    cache.write_text("1.1.0")  # Newer than current version "1.0.0"

    mock_console = MagicMock()

    with (
        patch(
            "google.agents.cli.scaffold.utils.version.get_current_version",
            return_value="1.0.0",
        ),
        patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen,
        patch("rich.console.Console", return_value=mock_console),
    ):
        version.display_update_message()

        # No background process spawned
        mock_popen.assert_not_called()
        # Message printed
        mock_console.print.assert_called()


def test_update_check_due_spawns_background_process(temp_paths):
    """Test that if update check is due, a background process is spawned and stamp is written."""
    stamp, cache = temp_paths
    # Stamp does not exist, so check is due

    with (
        patch(
            "google.agents.cli.scaffold.utils.version.get_current_version",
            return_value="1.0.0",
        ),
        patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen,
        patch("rich.console.Console") as mock_console_class,
    ):
        version.display_update_message()

        # Stamp file should now exist (written before spawn)
        assert stamp.exists()

        # Background process should be spawned
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        cmd = args[0]
        assert cmd[0] == sys.executable
        assert cmd[1] == "-c"
        assert "urllib.request" in cmd[2]
        assert "pypi" in cmd[2]

        # No message printed (since no version was in cache yet)
        mock_console_class.assert_not_called()
