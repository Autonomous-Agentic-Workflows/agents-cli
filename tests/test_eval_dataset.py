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

"""Unit tests for agents-cli eval dataset synthesize and generate command output formatting."""

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from google.agents.cli.eval.cmd_dataset import cmd_synthesize
from google.agents.cli.eval.cmd_generate import cmd_generate


def test_cmd_synthesize_success_output(tmp_path):
    # Setup mock project directory and manifest
    agent_dir = tmp_path / "app"
    agent_dir.mkdir()

    mock_cfg = MagicMock()
    mock_cfg.agent_directory = "app"

    runner = CliRunner()
    with patch("google.agents.cli.eval.cmd_dataset.find_project_root", return_value=tmp_path), \
         patch("google.agents.cli.eval.cmd_dataset.read_project_config", return_value=mock_cfg), \
         patch("google.agents.cli.eval.cmd_dataset.require_agent_directory"), \
         patch("google.agents.cli.eval.cmd_dataset._stage_synthesize_runner", return_value=tmp_path / "runner.py"), \
         patch("google.agents.cli.eval.cmd_dataset.run"):

        output_file = tmp_path / "traces.json"
        result = runner.invoke(cmd_synthesize, ["-o", str(output_file)])

        assert result.exit_code == 0
        assert "✓ Traces saved to:" in result.output


def test_cmd_generate_success_output(tmp_path):
    # Setup mock project directory and manifest
    agent_dir = tmp_path / "app"
    agent_dir.mkdir()

    mock_cfg = MagicMock()
    mock_cfg.agent_directory = "app"

    dataset_file = tmp_path / "dataset.json"
    dataset_file.write_text(json.dumps({"eval_cases": [{"prompt": "Hello"}]}), encoding="utf-8")

    runner = CliRunner()
    with patch("google.agents.cli.eval.cmd_generate.find_project_root", return_value=tmp_path), \
         patch("google.agents.cli.eval.cmd_generate.read_project_config", return_value=mock_cfg), \
         patch("google.agents.cli.eval.cmd_generate.require_agent_directory"), \
         patch("google.agents.cli.eval.cmd_generate._stage_inference_runner", return_value=tmp_path / "runner.py"), \
         patch("google.agents.cli.eval.cmd_generate.run"):

        output_file = tmp_path / "traces.json"
        result = runner.invoke(cmd_generate, ["--dataset", str(dataset_file), "-o", str(output_file)])

        assert result.exit_code == 0
        assert "✓ Traces saved to:" in result.output
