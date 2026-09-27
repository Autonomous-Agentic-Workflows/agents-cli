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

"""Tests for skills detection and npx package version pinning."""

from unittest.mock import MagicMock, patch

from google.agents.cli._skills_check import SKILLS_NPX_PACKAGE, _find_installed_skills
from google.agents.cli.setup.cmd_setup import _check_legacy_skills


def test_find_installed_skills_uses_pinned_npx_package(tmp_path):
    # Mock empty skill directories so it falls back to the slow path npx invocation
    with patch("google.agents.cli._skills_check.Path.home", return_value=tmp_path):
        with patch("google.agents.cli._skills_check.Path.cwd", return_value=tmp_path):
            with patch("google.agents.cli._runner.run_resolved") as mock_run:
                mock_proc = MagicMock()
                mock_proc.returncode = 0
                mock_proc.stdout = "[]"
                mock_run.return_value = mock_proc

                result = _find_installed_skills()
                assert result == {}
                mock_run.assert_called_once()
                args, _ = mock_run.call_args
                cmd = args[0]
                assert cmd == ["npx", "-y", SKILLS_NPX_PACKAGE, "list", "--json"]


def test_check_legacy_skills_uses_pinned_npx_package():
    with patch("google.agents.cli.setup.cmd_setup.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "[]"
        mock_run.return_value = mock_proc

        _check_legacy_skills()
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert cmd == ["npx", "-y", SKILLS_NPX_PACKAGE, "list", "--json"]
