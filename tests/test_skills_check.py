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

"""Unit tests for skills version drift detection and rate-limiting."""

from unittest.mock import patch

from google.agents.cli._skills_check import check_skills_version


def test_skills_check_records_stamp_when_no_skills(tmp_path, monkeypatch):
    """Verify that check_skills_version records stamp file even if no skills are installed."""
    stamp_file = tmp_path / ".acli_skills_check"
    monkeypatch.setattr(
        "google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp_file
    )
    monkeypatch.setattr("google.agents.cli._skills_check._is_ci", lambda: False)

    # Mock _find_installed_skills to return empty dict (no skills installed)
    with patch(
        "google.agents.cli._skills_check._find_installed_skills", return_value={}
    ) as mock_find:
        check_skills_version()
        assert mock_find.call_count == 1
        assert stamp_file.exists()

    # Second invocation should short-circuit and not call _find_installed_skills again
    with patch(
        "google.agents.cli._skills_check._find_installed_skills", return_value={}
    ) as mock_find_2:
        check_skills_version()
        assert mock_find_2.call_count == 0


def test_skills_check_skips_in_ci(tmp_path, monkeypatch):
    """Verify that check_skills_version skips execution when running in CI environment."""
    stamp_file = tmp_path / ".acli_skills_check"
    monkeypatch.setattr(
        "google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp_file
    )
    monkeypatch.setattr("google.agents.cli._skills_check._is_ci", lambda: True)

    with patch(
        "google.agents.cli._skills_check._find_installed_skills"
    ) as mock_find:
        check_skills_version()
        assert mock_find.call_count == 0
        assert not stamp_file.exists()


def test_skills_check_outputs_mismatched_skills(tmp_path, monkeypatch, capsys):
    """Verify that check_skills_version outputs warning when skill versions mismatch."""
    stamp_file = tmp_path / ".acli_skills_check"
    monkeypatch.setattr(
        "google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp_file
    )
    monkeypatch.setattr("google.agents.cli._skills_check._is_ci", lambda: False)
    monkeypatch.setattr("google.agents.cli.__version__", "1.2.1")

    installed_skills = {
        "google-agents-cli-adk-code": "1.1.0",
        "google-agents-cli-deploy": "1.2.1",
    }

    with patch(
        "google.agents.cli._skills_check._find_installed_skills",
        return_value=installed_skills,
    ):
        check_skills_version()

    captured = capsys.readouterr()
    assert "Skills version mismatch" in captured.out
    assert "google-agents-cli-adk-code (v1.1.0)" in captured.out
    assert "google-agents-cli-deploy" not in captured.out
