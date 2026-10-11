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

"""Tests for agents-cli deploy command confirmation prompt styling."""

from unittest.mock import MagicMock, patch
import click
from click.testing import CliRunner
from google.agents.cli.deploy.cmd_deploy import cmd_deploy


def test_deploy_project_confirmation_styled():
    """Verify that project confirmation prompt formats project ID in cyan bold."""
    runner = CliRunner()
    mock_cfg = MagicMock()
    mock_cfg.region = "us-central1"
    mock_cfg.deployment_target = "cloud_run"
    mock_cfg.agent_directory = "agent"

    project_id = "my-sample-gcp-project"
    styled_project = click.style(project_id, fg="cyan", bold=True)

    with (
        patch("google.agents.cli.deploy.cmd_deploy._load_deploy_config", return_value=(mock_cfg, True)),
        patch("google.agents.cli.deploy.cmd_deploy.resolve_gcp_project", return_value=project_id),
        patch("google.agents.cli.deploy.cmd_deploy._cloud_run_service_exists", return_value=True),
        patch("google.agents.cli.deploy.cmd_deploy._run_cloud_run_deploy_with_retry"),
        patch("google.agents.cli.deploy.cmd_deploy.read_project_dotenv", return_value={}),
        patch("google.agents.cli.deploy.cmd_deploy.get_project_version", return_value="0.1.0"),
        patch("google.agents.cli.deploy.cmd_deploy.run_resolved", return_value=MagicMock(stdout="123456")),
        patch("google.agents.cli.deploy.cmd_deploy._tools.require_tool"),
        patch("click.confirm", return_value=True) as mock_confirm,
    ):
        result = runner.invoke(cmd_deploy, ["-i"])
        assert result.exit_code == 0
        mock_confirm.assert_called_once()
        prompt_arg = mock_confirm.call_args[0][0]
        assert styled_project in prompt_arg
        assert f"Deploying to Google Cloud project '{styled_project}'. Proceed?" in prompt_arg
