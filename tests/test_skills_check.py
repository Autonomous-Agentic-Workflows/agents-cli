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

"""Tests for skills version drift check and rate limiting."""

import time
from unittest.mock import patch

from google.agents.cli._skills_check import check_skills_version, _skills_check_is_due


def test_skills_check_records_stamp_when_no_skills_installed(tmp_path, monkeypatch):
    """Verify that check_skills_version records stamp even when no skills are installed."""
    stamp_file = tmp_path / "stamp"
    monkeypatch.setattr("google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp_file)
    monkeypatch.setattr("google.agents.cli._skills_check._is_ci", lambda: False)
    monkeypatch.setattr("google.agents.cli._skills_check._find_installed_skills", lambda: {})

    assert not stamp_file.exists()
    assert _skills_check_is_due() is True

    check_skills_version()

    assert stamp_file.exists()
    assert _skills_check_is_due() is False


def test_skills_check_rate_limiting_prevents_rechecking(tmp_path, monkeypatch):
    """Verify that subsequent calls within interval do not re-run find_installed_skills."""
    stamp_file = tmp_path / "stamp"
    monkeypatch.setattr("google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp_file)
    monkeypatch.setattr("google.agents.cli._skills_check._is_ci", lambda: False)

    find_calls = 0

    def mock_find():
        nonlocal find_calls
        find_calls += 1
        return {}

    monkeypatch.setattr("google.agents.cli._skills_check._find_installed_skills", mock_find)

    # First call runs find_installed_skills and records stamp
    check_skills_version()
    assert find_calls == 1

    # Second call should short-circuit and not call find_installed_skills
    check_skills_version()
    assert find_calls == 1
