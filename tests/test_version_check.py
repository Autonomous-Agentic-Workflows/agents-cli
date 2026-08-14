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

"""Tests for non-blocking asynchronous version checking."""

import sys
from unittest.mock import MagicMock, patch

from google.agents.cli.scaffold.utils import version


def test_display_update_message_is_ci(monkeypatch):
    """Verify that version checks are completely skipped in CI environments."""
    monkeypatch.setattr(version, "_is_ci", lambda: True)

    called = False

    def mock_is_due():
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(version, "_update_check_is_due", mock_is_due)
    version.display_update_message()
    assert not called


def test_display_update_message_reads_cache(tmp_path, monkeypatch):
    """Verify that display_update_message displays update from cache if newer."""
    monkeypatch.setattr(version, "_is_ci", lambda: False)
    monkeypatch.setattr(version, "get_current_version", lambda: "1.0.0")

    cache_file = tmp_path / ".acli_latest_version"
    cache_file.write_text("1.1.0", encoding="utf-8")
    monkeypatch.setattr(version, "_LATEST_VERSION_CACHE", cache_file)

    # Set update check to NOT be due so we don't spawn background processes
    monkeypatch.setattr(version, "_update_check_is_due", lambda: False)

    # Mock Console to capture the print
    mock_console_inst = MagicMock()
    with patch("rich.console.Console", return_value=mock_console_inst):
        version.display_update_message()

    # Verify that console.print was called
    assert mock_console_inst.print.called


def test_display_update_message_spawns_background_check(tmp_path, monkeypatch):
    """Verify that display_update_message spawns background check when due."""
    monkeypatch.setattr(version, "_is_ci", lambda: False)
    monkeypatch.setattr(version, "get_current_version", lambda: "1.0.0")

    cache_file = tmp_path / ".acli_latest_version"
    monkeypatch.setattr(version, "_LATEST_VERSION_CACHE", cache_file)

    stamp_file = tmp_path / ".acli_update_check"
    monkeypatch.setattr(version, "_UPDATE_CHECK_STAMP", stamp_file)

    monkeypatch.setattr(version, "_update_check_is_due", lambda: True)

    spawn_called = False

    def mock_popen_resolved_detached(args, **kwargs):
        nonlocal spawn_called
        spawn_called = True
        assert sys.executable in args
        assert "-c" in args
        return None

    monkeypatch.setattr(
        "google.agents.cli._runner.popen_resolved_detached",
        mock_popen_resolved_detached,
    )

    version.display_update_message()

    assert spawn_called
    # It should have updated the stamp file locally to prevent concurrent spawn
    assert stamp_file.exists()
