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

"""Unit tests for skills version drift detection."""

from unittest.mock import patch

from google.agents.cli._skills_check import check_skills_version


def test_check_skills_version_skips_in_ci():
    """Verify check_skills_version early-returns when in CI."""
    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=True),
        patch(
            "google.agents.cli._skills_check._find_installed_skills"
        ) as mock_find,
    ):
        check_skills_version()
        mock_find.assert_not_called()


def test_check_skills_version_skips_when_not_due():
    """Verify check_skills_version early-returns when check is not due."""
    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=False),
        patch(
            "google.agents.cli._skills_check._skills_check_is_due",
            return_value=False,
        ),
        patch(
            "google.agents.cli._skills_check._find_installed_skills"
        ) as mock_find,
    ):
        check_skills_version()
        mock_find.assert_not_called()


def test_check_skills_version_outputs_formatted_warning():
    """Verify check_skills_version formats warning and skill list with proper colors."""
    mock_skills = {
        "google-agents-cli-adk-code": "1.1.0",
        "google-agents-cli-deploy": "1.1.0",
    }
    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=False),
        patch(
            "google.agents.cli._skills_check._skills_check_is_due",
            return_value=True,
        ),
        patch("google.agents.cli._skills_check._record_skills_check"),
        patch(
            "google.agents.cli._skills_check._find_installed_skills",
            return_value=mock_skills,
        ),
        patch("google.agents.cli.__version__", "1.2.1"),
        patch("click.secho") as mock_secho,
        patch("click.echo") as mock_echo,
    ):
        check_skills_version()

        mock_echo.assert_called_once()

        # Check warning header call
        header_call = mock_secho.call_args_list[0]
        assert "⚠️  Skills version mismatch — CLI is v1.2.1, but 2 skill(s) differ:" in header_call[0][0]
        assert header_call[1].get("fg") == "yellow"

        # Check skill detail calls
        skill1_call = mock_secho.call_args_list[1]
        assert "  - google-agents-cli-adk-code (v1.1.0)" in skill1_call[0][0]
        assert skill1_call[1].get("dim") is True

        skill2_call = mock_secho.call_args_list[2]
        assert "  - google-agents-cli-deploy (v1.1.0)" in skill2_call[0][0]
        assert skill2_call[1].get("dim") is True

        # Check sync advice call
        sync_call = mock_secho.call_args_list[3]
        assert "Run 'agents-cli update' to sync." in sync_call[0][0]
        assert sync_call[1].get("fg") == "yellow"


def test_check_skills_version_no_mismatch():
    """Verify check_skills_version stays silent when all skill versions match CLI."""
    mock_skills = {
        "google-agents-cli-adk-code": "1.2.1",
    }
    with (
        patch("google.agents.cli._skills_check._is_ci", return_value=False),
        patch(
            "google.agents.cli._skills_check._skills_check_is_due",
            return_value=True,
        ),
        patch("google.agents.cli._skills_check._record_skills_check"),
        patch(
            "google.agents.cli._skills_check._find_installed_skills",
            return_value=mock_skills,
        ),
        patch("google.agents.cli.__version__", "1.2.1"),
        patch("click.secho") as mock_secho,
    ):
        check_skills_version()
        mock_secho.assert_not_called()
