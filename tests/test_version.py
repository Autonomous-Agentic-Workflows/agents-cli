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

"""Tests for non-blocking version-checking and caching."""

import sys
from pathlib import Path
from unittest import mock

import pytest

from google.agents.cli.scaffold.utils import version


def test_display_update_message_not_due(tmp_path):
    stamp_file = tmp_path / ".acli_update_check"
    cache_file = tmp_path / ".acli_latest_version"

    # Write recent stamp so check is NOT due (e.g. current time)
    import time
    stamp_file.write_text(str(time.time()), encoding="utf-8")
    # Write latest version to cache
    cache_file.write_text("1.0.0", encoding="utf-8")

    with mock.patch("google.agents.cli.scaffold.utils.version._UPDATE_CHECK_STAMP", stamp_file), \
         mock.patch("google.agents.cli.scaffold.utils.version._LATEST_VERSION_CACHE", cache_file), \
         mock.patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         mock.patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen:

        version.display_update_message()

        # Should not spawn background process since it is not due
        mock_popen.assert_not_called()


def test_display_update_message_due_no_update(tmp_path):
    stamp_file = tmp_path / ".acli_update_check"
    cache_file = tmp_path / ".acli_latest_version"

    # Write old stamp so check is due
    stamp_file.write_text("0.0", encoding="utf-8")
    # Cache matches current version
    cache_file.write_text("1.0.0", encoding="utf-8")

    with mock.patch("google.agents.cli.scaffold.utils.version._UPDATE_CHECK_STAMP", stamp_file), \
         mock.patch("google.agents.cli.scaffold.utils.version._LATEST_VERSION_CACHE", cache_file), \
         mock.patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         mock.patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         mock.patch("rich.console.Console") as mock_console:

        version.display_update_message()

        # Should spawn background process because check is due
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert args[0] == sys.executable
        assert args[1] == "-c"
        assert "https://pypi.org/pypi/google-agents-cli/json" in args[2]

        # Console should not be called since there is no update (1.0.0 is not > 1.0.0)
        mock_console.assert_not_called()


def test_display_update_message_due_with_update(tmp_path):
    stamp_file = tmp_path / ".acli_update_check"
    cache_file = tmp_path / ".acli_latest_version"

    # Write old stamp so check is due
    stamp_file.write_text("0.0", encoding="utf-8")
    # Cache is newer than current version
    cache_file.write_text("1.5.0", encoding="utf-8")

    with mock.patch("google.agents.cli.scaffold.utils.version._UPDATE_CHECK_STAMP", stamp_file), \
         mock.patch("google.agents.cli.scaffold.utils.version._LATEST_VERSION_CACHE", cache_file), \
         mock.patch("google.agents.cli.scaffold.utils.version.get_current_version", return_value="1.0.0"), \
         mock.patch("google.agents.cli._runner.popen_resolved_detached") as mock_popen, \
         mock.patch("rich.console.Console") as mock_console:

        mock_instance = mock_console.return_value

        version.display_update_message()

        # Should spawn background process
        mock_popen.assert_called_once()
        # Should display update warning using rich Console
        mock_instance.print.assert_any_call(
            "\n[yellow]⚠️  Update available: 1.0.0 → 1.5.0[/]",
            highlight=False,
        )
