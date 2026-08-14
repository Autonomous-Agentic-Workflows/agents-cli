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

"""Tests for version checking utilities and caching."""

import sys
import time
from unittest.mock import MagicMock, patch

import pytest

from google.agents.cli.scaffold.utils import version


@pytest.fixture
def temp_cache_and_stamp(tmp_path):
    """Fixture to mock paths of latest version cache and update check stamp."""
    fake_cache = tmp_path / "acli_latest_version"
    fake_stamp = tmp_path / "acli_update_check"

    with patch.multiple(
        "google.agents.cli.scaffold.utils.version",
        _LATEST_VERSION_CACHE=fake_cache,
        _UPDATE_CHECK_STAMP=fake_stamp,
    ):
        yield fake_cache, fake_stamp


def test_display_update_message_no_cache_no_update(temp_cache_and_stamp):
    """If no cache exists, display_update_message should not print but should spawn bg check."""
    fake_cache, fake_stamp = temp_cache_and_stamp

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         patch("rich.console.Console") as mock_console:

        version.display_update_message()

        # No cache exists, so no print should happen
        mock_console.assert_not_called()

        # Since cache is missing, _update_check_is_due should return True, spawning bg check
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert sys.executable in args
        assert "-c" in args
        assert version.PACKAGE_NAME in args
        assert fake_cache.as_posix() in args
        assert fake_stamp.as_posix() in args


def test_display_update_message_with_cache_newer_version(temp_cache_and_stamp):
    """If cache exists with a newer version, it should print the update message."""
    fake_cache, fake_stamp = temp_cache_and_stamp
    fake_cache.write_text("1.1.0")
    fake_stamp.write_text(str(time.time()))  # Checked recently, not due

    mock_console_instance = MagicMock()

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         patch("rich.console.Console", return_value=mock_console_instance):

        version.display_update_message()

        # It should print update messages using Console
        mock_console_instance.print.assert_any_call(
            "\n[yellow]⚠️  Update available: 1.0.0 → 1.1.0[/]",
            highlight=False,
        )

        # Not due, so mock_popen should not be called
        mock_popen.assert_not_called()


def test_display_update_message_with_cache_same_version(temp_cache_and_stamp):
    """If cache exists but version is same/older, it should not print anything."""
    fake_cache, fake_stamp = temp_cache_and_stamp
    fake_cache.write_text("1.0.0")
    fake_stamp.write_text(str(time.time()))  # Checked recently

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         patch("rich.console.Console") as mock_console:

        version.display_update_message()

        mock_console.assert_not_called()
        mock_popen.assert_not_called()


def test_display_update_message_bg_check_due(temp_cache_and_stamp):
    """If cache exists and newer, and bg check is due, it should print AND trigger bg check."""
    fake_cache, fake_stamp = temp_cache_and_stamp
    fake_cache.write_text("1.1.0")
    # Stamp indicates check was 13 hours ago (due)
    fake_stamp.write_text(str(time.time() - (13 * 60 * 60)))

    mock_console_instance = MagicMock()

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         patch("rich.console.Console", return_value=mock_console_instance):

        version.display_update_message()

        # Should print update message
        mock_console_instance.print.assert_any_call(
            "\n[yellow]⚠️  Update available: 1.0.0 → 1.1.0[/]",
            highlight=False,
        )

        # Should trigger background check
        mock_popen.assert_called_once()
