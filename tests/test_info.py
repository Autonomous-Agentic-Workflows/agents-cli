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

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.info.cmd_info import cmd_info


def test_cmd_info_no_skills():
    runner = CliRunner()
    with patch("google.agents.cli.info.cmd_info.get_installed_skills", return_value=[]):
        result = runner.invoke(cmd_info)
        assert result.exit_code == 0
        assert "Installed skills:   none (run 'agents-cli setup' to install)" in result.output


def test_cmd_info_with_skills():
    runner = CliRunner()
    skills = [
        {"name": "test-skill", "scope": "project"}
    ]
    with patch("google.agents.cli.info.cmd_info.get_installed_skills", return_value=skills):
        result = runner.invoke(cmd_info)
        assert result.exit_code == 0
        assert "Installed skills:   1 (project)" in result.output
        assert "• test-skill" in result.output
