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

"""Tests for version checking utilities."""

from unittest.mock import MagicMock, patch

from google.agents.cli.scaffold.utils import version


def test_display_update_message_reads_cache_and_triggers_bg_check(
    tmp_path, monkeypatch
):
    # Mock cache and stamp paths to point to a temp directory
    cache_file = tmp_path / ".acli_latest_version"
    stamp_file = tmp_path / ".acli_update_check"

    monkeypatch.setattr(version, "_LATEST_VERSION_CACHE", cache_file)
    monkeypatch.setattr(version, "_UPDATE_CHECK_STAMP", stamp_file)
    monkeypatch.setattr(version, "get_current_version", lambda: "1.0.0")

    # Mock rich.console.Console
    mock_console_class = MagicMock()
    mock_console_instance = MagicMock()
    mock_console_class.return_value = mock_console_instance

    # Mock popen_resolved_detached
    mock_popen_resolved_detached = MagicMock()

    # 1. No cache, not due (mock stamp to be recent)
    stamp_file.write_text(str(version.time.time()), encoding="utf-8")

    with (
        patch("rich.console.Console", mock_console_class),
        patch(
            "google.agents.cli._runner.popen_resolved_detached",
            mock_popen_resolved_detached,
        ),
    ):
        version.display_update_message()

    mock_console_instance.print.assert_not_called()
    mock_popen_resolved_detached.assert_not_called()

    # 2. Cache exists (older/same version), not due
    cache_file.write_text("1.0.0", encoding="utf-8")
    with (
        patch("rich.console.Console", mock_console_class),
        patch(
            "google.agents.cli._runner.popen_resolved_detached",
            mock_popen_resolved_detached,
        ),
    ):
        version.display_update_message()

    mock_console_instance.print.assert_not_called()
    mock_popen_resolved_detached.assert_not_called()

    # 3. Cache exists (newer version), not due
    cache_file.write_text("1.1.0", encoding="utf-8")
    with (
        patch("rich.console.Console", mock_console_class),
        patch(
            "google.agents.cli._runner.popen_resolved_detached",
            mock_popen_resolved_detached,
        ),
    ):
        version.display_update_message()

    mock_console_instance.print.assert_called()
    mock_popen_resolved_detached.assert_not_called()

    # Reset mocks
    mock_console_instance.print.reset_mock()

    # 4. Due, should spawn background check and record check time
    # Make check due by deleting the stamp or making it old
    stamp_file.write_text("0.0", encoding="utf-8")

    with (
        patch("rich.console.Console", mock_console_class),
        patch(
            "google.agents.cli._runner.popen_resolved_detached",
            mock_popen_resolved_detached,
        ),
    ):
        version.display_update_message()

    # Check that update warning from "1.1.0" cache was still printed
    mock_console_instance.print.assert_called()
    # Check that popen_resolved_detached was called to spawn the background check
    mock_popen_resolved_detached.assert_called_once()
    # Check that timestamp was updated
    assert float(stamp_file.read_text(encoding="utf-8").strip()) > 0.0
