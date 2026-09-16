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

"""Tests for AGY command utilities and safe env loading."""

from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import bridge


def test_agy_bridge_vertex_env_parsing(tmp_path):
    env_file = tmp_path / "setup_enterprise_vertex_env.sh"
    env_file.write_text(
        "# Test comment\n"
        "export VERTEXAI_PROJECT='test-project-123'\n"
        "VERTEXAI_LOCATION=\"us-east1\"\n"
        "CUSTOM_VAR=custom_val\n",
        encoding="utf-8",
    )

    bridge_script = tmp_path / "bridge.py"
    bridge_script.write_text("print('bridge running')", encoding="utf-8")
    harness_bin = tmp_path / "localharness"
    harness_bin.write_text("dummy harness", encoding="utf-8")

    runner = CliRunner()
    with (
        patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_file)),
        patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_script)),
        patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_bin)),
        patch("subprocess.run") as mock_run,
    ):
        result = runner.invoke(bridge)
        assert result.exit_code == 0
        assert mock_run.called

        called_args, called_kwargs = mock_run.call_args
        env_passed = called_kwargs.get("env", {})

        assert env_passed.get("VERTEXAI_PROJECT") == "test-project-123"
        assert env_passed.get("VERTEXAI_LOCATION") == "us-east1"
        assert env_passed.get("CUSTOM_VAR") == "custom_val"
        assert "shell" not in called_kwargs
