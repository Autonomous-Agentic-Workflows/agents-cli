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

"""Tests to verify the update-checking caching mechanism and detached process creation."""

import time
from unittest.mock import MagicMock, patch
import pytest

import google.agents.cli.scaffold.utils.version as version_mod


@pytest.fixture
def mock_paths(tmp_path):
    """Fixture to redirect stamp and cache files to a temporary directory."""
    stamp_file = tmp_path / ".acli_update_check"
    cache_file = tmp_path / ".acli_latest_version"
    with patch.object(version_mod, "_UPDATE_CHECK_STAMP", stamp_file), \
         patch.object(version_mod, "_UPDATE_CHECK_LATEST_VERSION_FILE", cache_file):
        yield stamp_file, cache_file


def test_get_cached_latest_version_missing(mock_paths):
    """If the cache file does not exist, get_cached_latest_version should return UNKNOWN_VERSION."""
    _, cache_file = mock_paths
    assert not cache_file.exists()
    assert version_mod.get_cached_latest_version() == version_mod.UNKNOWN_VERSION


def test_get_cached_latest_version_exists(mock_paths):
    """If the cache file exists, get_cached_latest_version should return its contents."""
    _, cache_file = mock_paths
    cache_file.write_text("1.5.0", encoding="utf-8")
    assert version_mod.get_cached_latest_version() == "1.5.0"


def test_update_check_is_due(mock_paths):
    """Test _update_check_is_due under different conditions."""
    stamp_file, _ = mock_paths

    # Case 1: Stamp file doesn't exist yet -> Is due
    assert version_mod._update_check_is_due() is True

    # Case 2: Stamp file is brand new -> Not due
    version_mod._record_update_check()
    assert version_mod._update_check_is_due() is False

    # Case 3: Stamp file is 13 hours old -> Is due
    thirteen_hours_ago = time.time() - (13 * 60 * 60)
    stamp_file.write_text(str(thirteen_hours_ago), encoding="utf-8")
    assert version_mod._update_check_is_due() is True


@patch("google.agents.cli._runner.popen_resolved_detached")
def test_spawn_background_update_check(mock_popen, mock_paths):
    """Verify that _spawn_background_update_check spawns popen_resolved_detached correctly."""
    stamp_file, cache_file = mock_paths

    version_mod._spawn_background_update_check()

    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    cmd_args = args[0]

    # Verify that sys.executable is invoked with an inline script and paths as arguments
    assert cmd_args[1] == "-c"
    assert "urllib.request" in cmd_args[2]
    assert cmd_args[3] == str(cache_file)
    assert cmd_args[4] == str(stamp_file)
    assert kwargs.get("resolve_executable") is False


@patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0")
@patch("google.agents.cli.scaffold.utils.version._spawn_background_update_check")
@patch("rich.console.Console")
def test_display_update_message_no_update(mock_console_cls, mock_spawn, mock_get_current, mock_paths):
    """If cached version is older or same, no update message is displayed, but background check can spawn."""
    _, cache_file = mock_paths
    cache_file.write_text("1.0.0", encoding="utf-8")

    version_mod.display_update_message()

    # Console print should not be called because there's no update
    mock_console_cls.assert_not_called()
    # But spawn should be called because the check is due (no stamp exists yet)
    mock_spawn.assert_called_once()


@patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0")
@patch("google.agents.cli.scaffold.utils.version._spawn_background_update_check")
@patch("rich.console.Console")
def test_display_update_message_needs_update(mock_console_cls, mock_spawn, mock_get_current, mock_paths):
    """If cached version is newer, the update message is displayed via rich.Console."""
    _, cache_file = mock_paths
    cache_file.write_text("1.1.0", encoding="utf-8")

    # Mock the Console instance
    mock_console_inst = MagicMock()
    mock_console_cls.return_value = mock_console_inst

    version_mod.display_update_message()

    # Console print should be called with warning message
    mock_console_cls.assert_called()
    mock_console_inst.print.assert_called()
    printed_texts = "".join(call[0][0] for call in mock_console_inst.print.call_args_list)
    assert "Update available" in printed_texts
    assert "1.0.0 → 1.1.0" in printed_texts

    # Spawn should also be called because stamp doesn't exist
    mock_spawn.assert_called_once()


@patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0")
@patch("google.agents.cli.scaffold.utils.version._spawn_background_update_check")
@patch("rich.console.Console")
def test_display_update_message_not_due(mock_console_cls, mock_spawn, mock_get_current, mock_paths):
    """If check is not due, the background check is not spawned, but the cached warning is still shown."""
    _, cache_file = mock_paths
    cache_file.write_text("1.1.0", encoding="utf-8")

    # Record update check to make it not due
    version_mod._record_update_check()

    # Mock the Console instance
    mock_console_inst = MagicMock()
    mock_console_cls.return_value = mock_console_inst

    version_mod.display_update_message()

    # The warning should still be displayed based on cached latest version
    mock_console_inst.print.assert_called()

    # Spawn should NOT be called because it is not due
    mock_spawn.assert_not_called()
