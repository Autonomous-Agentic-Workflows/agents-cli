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

"""Unit tests for the skills version check system."""

import sys
from unittest.mock import patch, MagicMock

import pytest

from google.agents.cli import _skills_check


@pytest.fixture
def temp_paths(tmp_path):
    """Fixture to mock stamp path to point to tmp_path."""
    stamp = tmp_path / ".acli_skills_check"
    with patch("google.agents.cli._skills_check._SKILLS_CHECK_STAMP", stamp):
        yield stamp


def test_skills_check_not_due(temp_paths):
    """Test that if skills check is not due, _find_installed_skills is not called."""
    stamp = temp_paths
    stamp.write_text(str(_skills_check.time.time()))  # Just ran, so not due

    with patch("google.agents.cli._skills_check._find_installed_skills") as mock_find:
        _skills_check.check_skills_version()
        mock_find.assert_not_called()


def test_skills_check_due_no_skills_installed(temp_paths):
    """Test that if skills check is due and no skills are installed, stamp is still written."""
    stamp = temp_paths
    # Stamp does not exist, so check is due

    with (
        patch("google.agents.cli._skills_check._find_installed_skills", return_value={}) as mock_find,
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        # Stamp file should now exist (written because check was due)
        assert stamp.exists()
        mock_find.assert_called_once()
        mock_echo.assert_not_called()


def test_skills_check_due_skills_with_mismatch(temp_paths):
    """Test that if skills check is due and there are mismatching skills, warning is shown and stamp is written."""
    stamp = temp_paths

    mock_skills = {
        "google-agents-cli-adk-code": "1.1.0",
    }

    with (
        patch("google.agents.cli._skills_check._find_installed_skills", return_value=mock_skills),
        patch("google.agents.cli.__version__", "1.2.0"),
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        # Stamp file should be written
        assert stamp.exists()
        # Warning message should be shown via click.echo
        mock_echo.assert_called_once()
        args, _ = mock_echo.call_args
        assert "Skills version mismatch" in args[0]
        assert "google-agents-cli-adk-code (v1.1.0)" in args[0]


def test_skills_check_due_skills_matching(temp_paths):
    """Test that if skills check is due and skills are matching, no warning is shown but stamp is still written."""
    stamp = temp_paths

    mock_skills = {
        "google-agents-cli-adk-code": "1.2.0",
    }

    with (
        patch("google.agents.cli._skills_check._find_installed_skills", return_value=mock_skills),
        patch("google.agents.cli.__version__", "1.2.0"),
        patch("click.echo") as mock_echo,
    ):
        _skills_check.check_skills_version()

        # Stamp file should be written
        assert stamp.exists()
        mock_echo.assert_not_called()
