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

"""Tests to verify non-blocking update checking and caching."""

import time
from unittest.mock import MagicMock, patch
import pytest

from google.agents.cli.scaffold.utils import version


@pytest.fixture
def temp_paths(tmp_path):
    """Fixture to mock stamp and cache paths to temporary files."""
    stamp_path = tmp_path / ".acli_update_check"
    cache_path = tmp_path / ".acli_latest_version"

    with patch.object(version, "_UPDATE_CHECK_STAMP", stamp_path), \
         patch.object(version, "_LATEST_VERSION_CACHE", cache_path):
        yield stamp_path, cache_path


def test_no_update_if_no_cache(temp_paths):
    """Verify that no update message is displayed if cache file is missing."""
    stamp, cache = temp_paths
    assert not cache.exists()

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("rich.console.Console") as mock_console_cls, \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:

        # Mock check interval to not be due so we don't trigger the background spawn
        with patch("google.agents.cli.scaffold.utils.version._update_check_is_due", return_value=False):
            version.display_update_message()

        # No warning printed
        mock_console_cls.assert_not_called()
        mock_popen.assert_not_called()


def test_display_update_if_cache_newer(temp_paths):
    """Verify update warning is displayed if cache version is newer than current."""
    stamp, cache = temp_paths
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("1.1.0", encoding="utf-8")

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("rich.console.Console") as mock_console_cls, \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:

        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console

        # Mock check interval to not be due so we don't trigger spawn
        with patch("google.agents.cli.scaffold.utils.version._update_check_is_due", return_value=False):
            version.display_update_message()

        # Warning is printed because 1.1.0 > 1.0.0
        mock_console_cls.assert_called_once()
        mock_console.print.assert_any_call("\n[yellow]⚠️  Update available: 1.0.0 → 1.1.0[/]", highlight=False)
        mock_popen.assert_not_called()


def test_no_display_if_cache_older(temp_paths):
    """Verify no update warning is displayed if cache version is older or same."""
    stamp, cache = temp_paths
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("0.9.0", encoding="utf-8")

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("rich.console.Console") as mock_console_cls, \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:

        with patch("google.agents.cli.scaffold.utils.version._update_check_is_due", return_value=False):
            version.display_update_message()

        mock_console_cls.assert_not_called()
        mock_popen.assert_not_called()


def test_background_spawn_when_due(temp_paths):
    """Verify background spawn is triggered and stamp is updated when check is due."""
    stamp, cache = temp_paths
    assert not stamp.exists()

    with patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         patch("google.agents.cli.scaffold.utils.version._update_check_is_due", return_value=True):

        version.display_update_message()

        # Verify background process is spawned
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        # Executable list is passed
        cmd_args = args[0]
        assert "urllib.request" in cmd_args[2]  # script content has urllib.request
        assert kwargs["resolve_executable"] is False

        # Verify stamp was written
        assert stamp.exists()
        stamp_time = float(stamp.read_text().strip())
        assert time.time() - stamp_time < 5  # Stamp is fresh
