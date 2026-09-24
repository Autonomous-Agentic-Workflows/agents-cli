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

"""Tests for AGY command group."""

from unittest.mock import patch
from click.testing import CliRunner
from google.agents.cli.dev.cmd_agy import bridge


def test_agy_bridge_parses_vertex_env_file(tmp_path):
    env_file = tmp_path / "setup_vertex.sh"
    env_file.write_text("export TEST_VAR='hello_world'\nexport ANOTHER_VAR=123\n# comment\n", encoding="utf-8")

    bridge_file = tmp_path / "bridge.py"
    bridge_file.write_text("print('bridge')", encoding="utf-8")

    harness_file = tmp_path / "harness"
    harness_file.write_text("binary", encoding="utf-8")

    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_file)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_file)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_file)), \
         patch("subprocess.run") as mock_run:
        result = runner.invoke(bridge)
        assert result.exit_code == 0
        assert mock_run.called
        # Check environment passed to subprocess.run
        _, kwargs = mock_run.call_args
        passed_env = kwargs.get("env", {})
        assert passed_env.get("TEST_VAR") == "hello_world"
        assert passed_env.get("ANOTHER_VAR") == "123"
        # Verify shell=True was NOT used
        assert "shell" not in kwargs or kwargs["shell"] is False
