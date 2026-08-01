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

"""Tests for CLI update-checking and caching."""

import sys
import time
from unittest.mock import patch

import pytest

from google.agents.cli.scaffold.utils import version


@pytest.fixture
def mock_version_paths(tmp_path, monkeypatch):
    """Hermetic stamp and cache paths for version check testing."""
    stamp_path = tmp_path / ".acli_update_check"
    cache_path = tmp_path / ".acli_latest_version"

    monkeypatch.setattr(version, "_UPDATE_CHECK_STAMP", stamp_path)
    monkeypatch.setattr(version, "_LATEST_VERSION_CACHE", cache_path)

    return stamp_path, cache_path


def test_update_check_is_due(mock_version_paths):
    stamp_path, _ = mock_version_paths

    # Case 1: Stamp file does not exist -> due
    assert version._update_check_is_due() is True

    # Case 2: Stamp file is recent -> not due
    stamp_path.write_text(str(time.time()), encoding="utf-8")
    assert version._update_check_is_due() is False

    # Case 3: Stamp file is old -> due
    old_time = time.time() - (13 * 60 * 60)  # 13 hours ago
    stamp_path.write_text(str(old_time), encoding="utf-8")
    assert version._update_check_is_due() is True


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
@patch("google.agents.cli._runner.popen_resolved_detached")
def test_display_update_message_needs_update(
    mock_popen, mock_get_current, mock_version_paths, capsys
):
    stamp_path, cache_path = mock_version_paths

    mock_get_current.return_value = "1.0.0"
    # Write newer version to cache
    cache_path.write_text("1.1.0", encoding="utf-8")

    # Set stamp to be recent so we don't trigger background spawn, just verify cache reading
    stamp_path.write_text(str(time.time()), encoding="utf-8")

    # Call display_update_message
    version.display_update_message()

    # Verify that message printed to stdout (or stderr via rich Console)
    # Since Console writes to stdout by default under pytest, capsys captures it.
    captured = capsys.readouterr()
    assert "Update available: 1.0.0 → 1.1.0" in captured.out
    mock_popen.assert_not_called()


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
@patch("google.agents.cli._runner.popen_resolved_detached")
def test_display_update_message_up_to_date(
    mock_popen, mock_get_current, mock_version_paths, capsys
):
    stamp_path, cache_path = mock_version_paths

    mock_get_current.return_value = "1.1.0"
    # Write same version to cache
    cache_path.write_text("1.1.0", encoding="utf-8")
    stamp_path.write_text(str(time.time()), encoding="utf-8")

    version.display_update_message()

    captured = capsys.readouterr()
    assert "Update available" not in captured.out
    mock_popen.assert_not_called()


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
@patch("google.agents.cli._runner.popen_resolved_detached")
def test_display_update_message_spawns_background_if_due(
    mock_popen, mock_get_current, mock_version_paths
):
    stamp_path, cache_path = mock_version_paths

    mock_get_current.return_value = "1.0.0"
    # Stamp does not exist -> check is due!
    assert version._update_check_is_due() is True

    version.display_update_message()

    # Check stamp was written in foreground
    assert stamp_path.exists()
    assert float(stamp_path.read_text().strip()) <= time.time()

    # Verify background process was spawned
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    assert args[0][0] == sys.executable
    assert args[0][1] == "-c"
    # Verify script content
    script = args[0][2]
    assert "urllib.request" in script
    assert "https://pypi.org/pypi/google-agents-cli/json" in script
    assert str(cache_path.absolute()) in script
    assert kwargs.get("resolve_executable") is False
