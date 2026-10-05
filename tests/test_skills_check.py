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

"""Unit tests for skills version drift detection formatting and checks."""

import time
from unittest.mock import MagicMock, patch

import pytest

from google.agents.cli import _skills_check


@pytest.fixture
def temp_skills_stamp(tmp_path):
    """Fixture to mock stamp path to point to tmp_path."""
    stamp = tmp_path / ".acli_skills_check"
    with patch("google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp):
        yield stamp


def test_skills_check_skipped_in_ci(temp_skills_stamp, monkeypatch):
    """Test that check_skills_version skips execution when CI environment variables are present."""
    monkeypatch.setenv("CI", "true")

    with (
        patch("google.agents.cli._skills_check._find_installed_skills") as mock_find,
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        mock_find.assert_not_called()
        mock_echo.assert_not_called()


def test_skills_check_skipped_when_not_due(temp_skills_stamp):
    """Test that check_skills_version skips execution when timestamp indicates check is not due."""
    temp_skills_stamp.parent.mkdir(parents=True, exist_ok=True)
    temp_skills_stamp.write_text(str(time.time()))

    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=False),
        patch("google.agents.cli._skills_check._find_installed_skills") as mock_find,
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        mock_find.assert_not_called()
        mock_echo.assert_not_called()


def test_skills_check_matching_version(temp_skills_stamp):
    """Test that no warning is printed when installed skills match CLI version."""
    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=False),
        patch(
            "google.agents.cli._skills_check._find_installed_skills",
            return_value={"google-agents-cli-adk": "0.1.0"},
        ),
        patch("google.agents.cli.__version__", "0.1.0"),
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        assert temp_skills_stamp.exists()
        mock_echo.assert_not_called()


def test_skills_check_mismatched_version_formatting(temp_skills_stamp):
    """Test that warning is formatted with styling when skill versions mismatch."""
    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=False),
        patch(
            "google.agents.cli._skills_check._find_installed_skills",
            return_value={
                "google-agents-cli-adk": "0.0.9",
                "google-agents-cli-rag": "0.1.0",
            },
        ),
        patch("google.agents.cli.__version__", "0.1.0"),
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        assert temp_skills_stamp.exists()
        mock_echo.assert_called_once()
        output_arg = mock_echo.call_args[0][0]
        assert "Skills version mismatch" in output_arg
        assert "CLI is v0.1.0" in output_arg
        assert "1 skill(s) differ" in output_arg
        assert "google-agents-cli-adk (v0.0.9)" in output_arg
        assert "agents-cli update" in output_arg
