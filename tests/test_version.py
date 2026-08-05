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

"""Unit tests for non-blocking update checking mechanism."""

import sys
import time
from unittest.mock import MagicMock, patch
import pytest

from google.agents.cli.scaffold.utils import version


@pytest.fixture
def mock_paths(tmp_path):
    stamp_file = tmp_path / "acli_update_check"
    cache_file = tmp_path / "acli_latest_version"
    with (
        patch.object(version, "_UPDATE_CHECK_STAMP", stamp_file),
        patch.object(version, "_LATEST_VERSION_CACHE", cache_file),
    ):
        yield stamp_file, cache_file


@pytest.fixture
def mock_current_version():
    with patch(
        "google.agents.cli.scaffold.utils.version.get_current_version",
        return_value="1.0.0",
    ):
        yield "1.0.0"


@pytest.fixture
def mock_popen_detached():
    with patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:
        yield mock_popen


def test_display_update_message_no_cache_due(
    mock_paths, mock_current_version, mock_popen_detached
):
    stamp_file, cache_file = mock_paths

    with patch("rich.console.Console") as mock_console:
        version.display_update_message()

        # Verify no console warning was printed because cache is empty
        mock_console.assert_not_called()

        # Verify stamp file was written indicating check has been recorded
        assert stamp_file.is_file()

        # Verify background process was spawned to query PyPI
        mock_popen_detached.assert_called_once()
        args, kwargs = mock_popen_detached.call_args
        assert args[0][0] == sys.executable
        assert "-c" in args[0]
        assert "google-agents-cli" in args[0]
        assert str(cache_file) in args[0]


def test_display_update_message_cached_up_to_date_due(
    mock_paths, mock_current_version, mock_popen_detached
):
    stamp_file, cache_file = mock_paths
    cache_file.write_text("1.0.0", encoding="utf-8")

    with patch("rich.console.Console") as mock_console:
        version.display_update_message()

        mock_console.assert_not_called()
        assert stamp_file.is_file()
        mock_popen_detached.assert_called_once()


def test_display_update_message_cached_newer_not_due(
    mock_paths, mock_current_version, mock_popen_detached
):
    stamp_file, cache_file = mock_paths
    cache_file.write_text("1.1.0", encoding="utf-8")
    stamp_file.write_text(str(time.time()), encoding="utf-8")

    mock_console_inst = MagicMock()
    with patch("rich.console.Console", return_value=mock_console_inst):
        version.display_update_message()

        # Verify warning was printed since cached version is newer
        mock_console_inst.print.assert_called()

        # Verify no background process was spawned since check is not due
        mock_popen_detached.assert_not_called()


def test_display_update_message_cached_newer_due(
    mock_paths, mock_current_version, mock_popen_detached
):
    stamp_file, cache_file = mock_paths
    cache_file.write_text("1.1.0", encoding="utf-8")
    stamp_file.write_text(str(time.time() - 24 * 60 * 60), encoding="utf-8")

    mock_console_inst = MagicMock()
    with patch("rich.console.Console", return_value=mock_console_inst):
        version.display_update_message()

        # Verify warning was printed since cached version is newer
        mock_console_inst.print.assert_called()

        # Verify background process was spawned to refresh cache
        mock_popen_detached.assert_called_once()
