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

"""Tests for agents-cli deploy command."""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from google.agents.cli.deploy.cmd_deploy import cmd_deploy


def test_deploy_interactive_by_default():
    """Verify that 'deploy' command defaults to interactive mode and prompts for project confirmation."""
    runner = CliRunner()
    mock_cfg = MagicMock()
    mock_cfg.region = "us-central1"
    mock_cfg.deployment_target = "cloud_run"

    with (
        patch("google.agents.cli.deploy.cmd_deploy._load_deploy_config", return_value=(mock_cfg, True)),
        patch("google.agents.cli.deploy.cmd_deploy._resolve_deploy_service_name", return_value="my-service"),
        patch("google.agents.cli.deploy.cmd_deploy.resolve_gcp_project", return_value="my-project-123"),
        patch("click.confirm", return_value=False) as mock_confirm,
    ):
        result = runner.invoke(cmd_deploy, ["--dry-run"])
        assert result.exit_code != 0
        assert "Aborted by user" in result.output
        mock_confirm.assert_called_once_with("Deploying to Google Cloud project 'my-project-123'. Proceed?", default=True)


def test_deploy_no_interactive_requires_explicit_confirmation():
    """Verify that 'deploy --no-interactive' raises an error requiring explicit project or confirmation flag."""
    runner = CliRunner()
    mock_cfg = MagicMock()
    mock_cfg.region = "us-central1"
    mock_cfg.deployment_target = "cloud_run"

    with (
        patch("google.agents.cli.deploy.cmd_deploy._load_deploy_config", return_value=(mock_cfg, True)),
        patch("google.agents.cli.deploy.cmd_deploy._resolve_deploy_service_name", return_value="my-service"),
        patch("google.agents.cli.deploy.cmd_deploy.resolve_gcp_project", return_value="my-project-123"),
        patch("click.confirm") as mock_confirm,
    ):
        result = runner.invoke(cmd_deploy, ["--no-interactive", "--dry-run"])
        assert result.exit_code != 0
        assert "confirmation required" in result.output
        mock_confirm.assert_not_called()
