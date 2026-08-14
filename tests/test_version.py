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

"""Unit tests for the CLI non-blocking update checking mechanism."""

from pathlib import Path
import time
from unittest.mock import MagicMock, patch

import pytest

import google.agents.cli.scaffold.utils.version as version_mod


@pytest.fixture
def mock_version_paths(tmp_path):
    """Fixture to mock paths for stamps and caches, ensuring no side effects on user directories."""
    orig_cache = version_mod._LATEST_VERSION_CACHE
    orig_stamp = version_mod._UPDATE_CHECK_STAMP

    version_mod._LATEST_VERSION_CACHE = tmp_path / "acli_latest_version"
    version_mod._UPDATE_CHECK_STAMP = tmp_path / "acli_update_check"

    yield tmp_path

    version_mod._LATEST_VERSION_CACHE = orig_cache
    version_mod._UPDATE_CHECK_STAMP = orig_stamp


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_unknown_version(mock_get_current, mock_version_paths):
    """Ensure update checking is skipped on unknown (dev/local) versions."""
    mock_get_current.return_value = "0.0.0"

    # Set cached version to something newer to see if it triggers warning (it shouldn't)
    version_mod._LATEST_VERSION_CACHE.write_text("1.0.0", encoding="utf-8")

    with patch("rich.console.Console") as mock_console_cls:
        version_mod.display_update_message()
        mock_console_cls.assert_not_called()


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_not_due_no_update(mock_get_current, mock_version_paths):
    """Ensure no message is printed when not due and current >= cached."""
    mock_get_current.return_value = "1.2.0"
    version_mod._LATEST_VERSION_CACHE.write_text("1.2.0", encoding="utf-8")

    # Set stamp to not due (e.g., checked 5 minutes ago)
    version_mod._UPDATE_CHECK_STAMP.write_text(str(time.time() - 300), encoding="utf-8")

    with patch("rich.console.Console") as mock_console_cls:
        with patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:
            version_mod.display_update_message()
            mock_console_cls.assert_not_called()
            mock_popen.assert_not_called()


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_not_due_with_update(mock_get_current, mock_version_paths):
    """Ensure update message is printed from cache even if check is not due."""
    mock_get_current.return_value = "1.2.0"
    version_mod._LATEST_VERSION_CACHE.write_text("1.3.0", encoding="utf-8")

    # Set stamp to not due (e.g., checked 5 minutes ago)
    version_mod._UPDATE_CHECK_STAMP.write_text(str(time.time() - 300), encoding="utf-8")

    # Mock rich Console instance
    mock_console = MagicMock()
    with patch("rich.console.Console", return_value=mock_console):
        with patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:
            version_mod.display_update_message()

            # Ensure warning printed
            mock_console.print.assert_any_call(
                "\n[yellow]⚠️  Update available: 1.2.0 → 1.3.0[/]",
                highlight=False,
            )
            # Ensure background process was NOT spawned
            mock_popen.assert_not_called()


@patch("google.agents.cli.scaffold.utils.version.get_current_version")
def test_display_update_message_due_spawns_bg(mock_get_current, mock_version_paths):
    """Ensure background process is spawned and stamp updated when check is due."""
    mock_get_current.return_value = "1.2.0"
    version_mod._LATEST_VERSION_CACHE.write_text("1.2.0", encoding="utf-8")

    # Set stamp to due (checked 24 hours ago)
    version_mod._UPDATE_CHECK_STAMP.write_text(str(time.time() - 24 * 3600), encoding="utf-8")

    with patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:
        version_mod.display_update_message()

        # Check that timestamp stamp was updated
        stamp_time = float(version_mod._UPDATE_CHECK_STAMP.read_text().strip())
        assert time.time() - stamp_time < 5  # Stamp was updated just now

        # Check that popen_resolved_detached was called to spawn bg script
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        cmd = args[0]
        assert "urllib.request" in cmd[2]
        assert "pypi.org" in cmd[2]
        assert kwargs.get("resolve_executable") is False
