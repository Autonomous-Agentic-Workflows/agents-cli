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

"""Tests to verify update-checking non-blocking background logic."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from google.agents.cli.scaffold.utils import version


@pytest.fixture
def mock_stamp_and_cache_files(tmp_path):
    """Fixture to mock paths used in version utilities."""
    stamp_file = tmp_path / "acli_update_check"
    cache_file = tmp_path / "acli_latest_version"

    with patch.object(version, "_UPDATE_CHECK_STAMP", stamp_file), \
         patch.object(version, "_LATEST_VERSION_CACHE", cache_file):
        yield stamp_file, cache_file


def test_update_check_is_due_missing(mock_stamp_and_cache_files):
    """Test that update check is due when the stamp file is missing."""
    assert version._update_check_is_due() is True


def test_update_check_is_due_recent(mock_stamp_and_cache_files):
    """Test that update check is NOT due if stamp file was recently updated."""
    stamp_file, _ = mock_stamp_and_cache_files
    import time
    stamp_file.write_text(str(time.time() - 100))
    assert version._update_check_is_due() is False


def test_update_check_is_due_old(mock_stamp_and_cache_files):
    """Test that update check is due if stamp file is older than interval."""
    stamp_file, _ = mock_stamp_and_cache_files
    import time
    stamp_file.write_text(str(time.time() - version._UPDATE_CHECK_INTERVAL - 10))
    assert version._update_check_is_due() is True


@patch("google.agents.cli._runner.popen_resolved_detached")
@patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0")
@patch("rich.console.Console")
def test_display_update_message_spawns_when_due(
    mock_console_class, mock_get_curr, mock_popen, mock_stamp_and_cache_files
):
    """Test that display_update_message spawns background subprocess when check is due."""
    stamp_file, cache_file = mock_stamp_and_cache_files

    # Ensure check is due
    assert version._update_check_is_due() is True

    # No cache exists initially, so no message should be printed
    mock_console_instance = MagicMock()
    mock_console_class.return_value = mock_console_instance

    version.display_update_message()

    # It should have updated the stamp file to mark check as handled
    assert version._update_check_is_due() is False
    assert stamp_file.is_file()

    # It should have called popen_resolved_detached to trigger the background update
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    cmd_list = args[0]
    assert cmd_list[0] == version.sys.executable
    assert "-c" in cmd_list
    assert str(cache_file) in cmd_list

    # No console messages should be printed since cache file was empty
    mock_console_instance.print.assert_not_called()


@patch("google.agents.cli._runner.popen_resolved_detached")
@patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0")
@patch("rich.console.Console")
def test_display_update_message_prints_from_cache(
    mock_console_class, mock_get_curr, mock_popen, mock_stamp_and_cache_files
):
    """Test that display_update_message displays update message from cache and is non-blocking."""
    stamp_file, cache_file = mock_stamp_and_cache_files

    # Write old stamp so check is NOT due, thus avoiding spawning background process
    import time
    stamp_file.write_text(str(time.time()))

    # Write a newer version to the cache
    cache_file.write_text("1.1.0", encoding="utf-8")

    mock_console_instance = MagicMock()
    mock_console_class.return_value = mock_console_instance

    version.display_update_message()

    # No background process spawned
    mock_popen.assert_not_called()

    # Print should have been called since 1.1.0 > 1.0.0
    mock_console_instance.print.assert_called()
    printed_texts = [call[0][0] for call in mock_console_instance.print.call_args_list]
    assert any("Update available: 1.0.0 → 1.1.0" in text for text in printed_texts)
