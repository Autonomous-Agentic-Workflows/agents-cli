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

import json
from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli.info.cmd_info import cmd_info


def test_cmd_info_no_project(tmp_path):
    """Test `agents-cli info` when outside an agent project."""
    runner = CliRunner()
    with patch("google.agents.cli.info.cmd_info.find_project_root", return_value=None), patch(
        "google.agents.cli.info.cmd_info.get_installed_skills", return_value=[]
    ):
        result = runner.invoke(cmd_info)
        assert result.exit_code == 0
        assert "CLI version:" in result.output
        assert "No agent project found" in result.output


def test_cmd_info_no_project_json():
    """Test `agents-cli info --json` when outside an agent project."""
    runner = CliRunner()
    with patch("google.agents.cli.info.cmd_info.find_project_root", return_value=None), patch(
        "google.agents.cli.info.cmd_info.get_installed_skills", return_value=[]
    ):
        result = runner.invoke(cmd_info, ["--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "cli_version" in data
        assert data["project"] is None


def test_cmd_info_with_project(tmp_path):
    """Test `agents-cli info` inside an agent project."""
    runner = CliRunner()
    fake_root = tmp_path / "my_project"
    fake_root.mkdir()

    class FakeConfig:
        project_name = "test-agent"
        deployment_target = "cloud_run"
        agent_directory = "agent"
        is_a2a = True
        region = "us-central1"
        cli_version = "1.2.1"

    with patch("google.agents.cli.info.cmd_info.find_project_root", return_value=fake_root), patch(
        "google.agents.cli.info.cmd_info.read_project_config", return_value=FakeConfig()
    ), patch("google.agents.cli.info.cmd_info.check_cli_version"), patch(
        "google.agents.cli.info.cmd_info.get_installed_skills",
        return_value=[{"name": "test-skill", "scope": "global"}],
    ):
        result = runner.invoke(cmd_info)
        assert result.exit_code == 0
        assert "CLI version:" in result.output
        assert "Project root:" in result.output
        assert "test-agent" in result.output
        assert "cloud_run" in result.output
        assert "yes" in result.output
