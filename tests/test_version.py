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

"""Unit tests for the CLI update-checking system in version.py."""

import sys
import time
from unittest.mock import patch, MagicMock

import pytest

from google.agents.cli.scaffold.utils.version import display_update_message


@pytest.fixture
def mock_version_paths(tmp_path):
    """Fixture to mock stamp and cache files to a temp directory."""
    stamp_path = tmp_path / "acli_update_check"
    cache_path = tmp_path / "acli_latest_version"
    with (
        patch(
            "google.agents.cli.scaffold.utils.version._UPDATE_CHECK_STAMP", stamp_path
        ),
        patch(
            "google.agents.cli.scaffold.utils.version._LATEST_VERSION_CACHE", cache_path
        ),
    ):
        yield stamp_path, cache_path


@pytest.fixture
def mock_dependencies():
    """Fixture to mock external calls like current version and process spawning."""
    with (
        patch(
            "google.agents.cli.scaffold.utils.version.get_current_version",
            return_value="1.0.0",
        ) as mock_get_current,
        patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen,
        patch("rich.console.Console") as mock_console_cls,
    ):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console
        yield mock_get_current, mock_popen, mock_console


def test_display_update_message_not_due_no_cache(mock_version_paths, mock_dependencies):
    """If update check is not due and cache is missing, nothing should happen."""
    stamp_path, cache_path = mock_version_paths
    mock_get_current, mock_popen, mock_console = mock_dependencies

    # Write a recent timestamp to make check not due
    stamp_path.write_text(str(time.time()))

    display_update_message()

    # No version comparison printed, no background task spawned
    mock_console.print.assert_not_called()
    mock_popen.assert_not_called()


def test_display_update_message_not_due_with_older_cache(
    mock_version_paths, mock_dependencies
):
    """If update check is not due and cached version is older/same, do not show warning."""
    stamp_path, cache_path = mock_version_paths
    mock_get_current, mock_popen, mock_console = mock_dependencies

    # Setup state
    stamp_path.write_text(str(time.time()))
    cache_path.write_text("0.9.0")  # Older than current (1.0.0)

    display_update_message()

    mock_console.print.assert_not_called()
    mock_popen.assert_not_called()


def test_display_update_message_not_due_with_newer_cache(
    mock_version_paths, mock_dependencies
):
    """If update check is not due but cached version is newer, display update warning instantly."""
    stamp_path, cache_path = mock_version_paths
    mock_get_current, mock_popen, mock_console = mock_dependencies

    # Setup state
    stamp_path.write_text(str(time.time()))
    cache_path.write_text("2.0.0")  # Newer than current (1.0.0)

    display_update_message()

    # Warning printed
    assert mock_console.print.call_count > 0
    # No background check spawned (since not due)
    mock_popen.assert_not_called()


def test_display_update_message_due_no_cache(mock_version_paths, mock_dependencies):
    """If update check is due and cache is missing, spawn background checker and record time."""
    stamp_path, cache_path = mock_version_paths
    mock_get_current, mock_popen, mock_console = mock_dependencies

    # No timestamp written -> check is due

    display_update_message()

    # No warning printed because there's no cache
    mock_console.print.assert_not_called()

    # Background checker spawned
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    # Check that Python executable and -c is used to run the inline updater
    assert args[0][0] == sys.executable
    assert args[0][1] == "-c"
    # Ensure urllib.request is mentioned in the code snippet
    assert "urllib.request" in args[0][2]

    # Timestamp recorded
    assert stamp_path.is_file()
    assert float(stamp_path.read_text().strip()) <= time.time()


def test_display_update_message_due_with_newer_cache(
    mock_version_paths, mock_dependencies
):
    """If update check is due and cache has a newer version, show warning AND spawn background checker."""
    stamp_path, cache_path = mock_version_paths
    mock_get_current, mock_popen, mock_console = mock_dependencies

    # Write old stamp so check is due
    stamp_path.write_text(str(time.time() - 24 * 60 * 60))
    cache_path.write_text("1.5.0")  # Newer than current (1.0.0)

    display_update_message()

    # Warning printed
    assert mock_console.print.call_count > 0
    # Background checker spawned
    mock_popen.assert_called_once()
    # Timestamp updated
    assert float(stamp_path.read_text().strip()) > time.time() - 60
