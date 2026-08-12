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

"""Tests for version checking and non-blocking background update checking."""

import sys
import time
from unittest.mock import MagicMock, patch
import pytest

from google.agents.cli.scaffold.utils import version as version_mod


@pytest.fixture
def mock_version_paths(tmp_path, monkeypatch):
    """Override cache and stamp paths to point to a temporary folder."""
    stamp_path = tmp_path / ".acli_update_check"
    cache_path = tmp_path / ".acli_latest_version"
    monkeypatch.setattr(version_mod, "_UPDATE_CHECK_STAMP", stamp_path)
    monkeypatch.setattr(version_mod, "_LATEST_VERSION_CACHE", cache_path)
    return stamp_path, cache_path


def test_update_check_is_due(mock_version_paths):
    stamp_path, _ = mock_version_paths

    # Case 1: Stamp file does not exist -> due
    assert version_mod._update_check_is_due() is True

    # Case 2: Stamp file is old -> due
    stamp_path.write_text(str(time.time() - 13 * 60 * 60))  # 13 hours ago
    assert version_mod._update_check_is_due() is True

    # Case 3: Stamp file is recent -> not due
    stamp_path.write_text(str(time.time() - 1 * 60 * 60))  # 1 hour ago
    assert version_mod._update_check_is_due() is False


def test_record_update_check(mock_version_paths):
    stamp_path, _ = mock_version_paths
    assert not stamp_path.exists()

    version_mod._record_update_check()
    assert stamp_path.exists()
    timestamp = float(stamp_path.read_text().strip())
    assert abs(time.time() - timestamp) < 5


@patch("google.agents.cli._runner.popen_resolved_detached")
@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_no_update_needed(
    mock_get_current, mock_popen, mock_version_paths
):
    stamp_path, cache_path = mock_version_paths
    mock_get_current.return_value = "1.0.0"

    # Set stamp to recent so we don't spawn background check
    stamp_path.write_text(str(time.time()))

    # Write old/matching version to cache
    cache_path.write_text("1.0.0")

    # Capture print/console
    mock_console_print = MagicMock()
    with patch("rich.console.Console") as mock_console:
        mock_console.return_value.print = mock_console_print
        version_mod.display_update_message()

    # Should not print any warning
    mock_console_print.assert_not_called()
    mock_popen.assert_not_called()


@patch("google.agents.cli._runner.popen_resolved_detached")
@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_update_available(
    mock_get_current, mock_popen, mock_version_paths
):
    stamp_path, cache_path = mock_version_paths
    mock_get_current.return_value = "1.0.0"

    # Set stamp to recent so we don't spawn background check
    stamp_path.write_text(str(time.time()))

    # Write newer version to cache
    cache_path.write_text("1.1.0")

    mock_console_print = MagicMock()
    with patch("rich.console.Console") as mock_console:
        mock_console.return_value.print = mock_console_print
        version_mod.display_update_message()

    # Should print update warnings
    mock_console_print.assert_any_call(
        "\n[yellow]⚠️  Update available: 1.0.0 → 1.1.0[/]",
        highlight=False,
    )
    mock_popen.assert_not_called()


@patch("google.agents.cli._runner.popen_resolved_detached")
@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_spawns_detached_process(
    mock_get_current, mock_popen, mock_version_paths
):
    stamp_path, cache_path = mock_version_paths
    mock_get_current.return_value = "1.0.0"

    # Ensure check is due
    if stamp_path.exists():
        stamp_path.unlink()

    # Clear cache
    if cache_path.exists():
        cache_path.unlink()

    with patch("rich.console.Console") as mock_console:
        version_mod.display_update_message()

    # Should record stamp immediately to prevent multiple spawns
    assert stamp_path.exists()

    # Should have called popen_resolved_detached
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    cmd = args[0]
    assert cmd[0] == sys.executable
    assert cmd[1] == "-c"
    assert "urllib.request" in cmd[2]
    assert "google-agents-cli" in cmd[2]
    assert kwargs.get("resolve_executable") is False
