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

import subprocess
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import VERTEX_ENV, bridge


def test_bridge_sources_vertex_env_safely():
    runner = CliRunner()

    def mock_exists(path):
        return True

    def mock_run(cmd, **kwargs):
        res = MagicMock()
        res.returncode = 0
        if cmd[0] == "/bin/bash":
            res.stdout = "TEST_VAR_FROM_VERTEX=hello_world\n"
        else:
            res.stdout = ""
        return res

    with (
        patch("os.path.exists", side_effect=mock_exists),
        patch("subprocess.run", side_effect=mock_run) as mock_subprocess,
    ):
        result = runner.invoke(bridge)
        assert result.exit_code == 0

        # Check first subprocess call (sourcing VERTEX_ENV safely without shell=True)
        bash_call = mock_subprocess.call_args_list[0]
        args, kwargs = bash_call
        assert args[0] == ["/bin/bash", "-c", 'source "$1" && env', "_", VERTEX_ENV]
        assert kwargs.get("shell") is not True

        # Check second subprocess call launched bridge script with updated environment
        bridge_call = mock_subprocess.call_args_list[1]
        _, bridge_kwargs = bridge_call
        env_passed = bridge_kwargs.get("env", {})
        assert env_passed.get("TEST_VAR_FROM_VERTEX") == "hello_world"
