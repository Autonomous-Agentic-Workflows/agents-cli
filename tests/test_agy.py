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

"""Tests for agy command module."""

from unittest.mock import patch
from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import bridge


def test_bridge_vertex_env_parsing(tmp_path):
    """Test that VERTEX_ENV file is parsed without shell=True execution."""
    env_file = tmp_path / "setup_vertex.sh"
    env_file.write_text(
        "# Comment line\n"
        "export GOOGLE_CLOUD_PROJECT=test-project-123\n"
        "VERTEXAI_LOCATION='us-east1'\n"
        "CUSTOM_KEY=\"custom_value\"\n",
        encoding="utf-8",
    )

    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_file)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(tmp_path / "bridge.py")), \
         patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(tmp_path / "harness")), \
         patch("os.path.exists", return_value=True), \
         patch("subprocess.run") as mock_subproc_run:
        result = runner.invoke(bridge)
        assert result.exit_code == 0, f"Command failed with output: {result.output}"

        # Verify subprocess.run was called once for python bridge execution without shell=True
        assert mock_subproc_run.call_count == 1
        args, kwargs = mock_subproc_run.call_args
        assert "shell" not in kwargs or kwargs["shell"] is False
        env = kwargs.get("env", {})
        assert env.get("GOOGLE_CLOUD_PROJECT") == "test-project-123"
        assert env.get("VERTEXAI_LOCATION") == "us-east1"
        assert env.get("CUSTOM_KEY") == "custom_value"
