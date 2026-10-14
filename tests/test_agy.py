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

"""Tests for agents-cli agy command."""

import subprocess
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from google.agents.cli.dev.cmd_agy import agy, VERTEX_ENV, AGY_BRIDGE, AGY_HARNESS


def test_agy_bridge_vertex_env_sourcing_without_shell_true():
    """Verify VERTEX_ENV is sourced safely using parameterized bash without shell=True."""
    runner = CliRunner()

    def mock_exists(path):
        if path in (AGY_BRIDGE, AGY_HARNESS, VERTEX_ENV):
            return True
        return False

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("subprocess.run") as mock_run:
            mock_res = MagicMock()
            mock_res.stdout = "TEST_SOUCED_VAR=hello_world\nOTHER_VAR=123"
            mock_run.side_effect = [mock_res, MagicMock()]

            result = runner.invoke(agy, ["bridge"])

            assert result.exit_code == 0
            assert mock_run.call_count == 2

            # Check first subprocess call (sourcing VERTEX_ENV)
            first_call = mock_run.call_args_list[0]
            cmd = first_call[0][0]
            kwargs = first_call[1]

            assert cmd == ["/bin/bash", "-c", 'source "$1" && env', "_", VERTEX_ENV]
            assert "shell" not in kwargs or kwargs["shell"] is False

            # Check second subprocess call (executing AGY bridge script)
            second_call = mock_run.call_args_list[1]
            env_passed = second_call[1].get("env", {})
            assert env_passed.get("TEST_SOUCED_VAR") == "hello_world"
            assert env_passed.get("OTHER_VAR") == "123"
