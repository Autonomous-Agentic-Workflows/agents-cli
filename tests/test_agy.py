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

"""Tests for agy CLI commands and shell execution security."""

import shlex
from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import bridge


def test_agy_bridge_vertex_env_quoting(tmp_path):
    env_file = tmp_path / "setup env; echo injected.sh"
    env_file.touch()

    bridge_file = tmp_path / "bridge.py"
    bridge_file.touch()

    harness_file = tmp_path / "localharness"
    harness_file.touch()

    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_file)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_file)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_file)), \
         patch("subprocess.run") as mock_run:
        result = runner.invoke(bridge)
        assert result.exit_code == 0
        expected_cmd = f"source {shlex.quote(str(env_file))}"
        assert any(
            call.args and call.args[0] == expected_cmd
            for call in mock_run.call_args_list
        )
