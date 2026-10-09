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

"""Tests for google.agents.cli.dev.cmd_agy command module."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import bridge


def test_bridge_sourcing_vertex_env_without_shell_true(tmp_path):
    vertex_env_script = tmp_path / "setup_vertex.sh"
    vertex_env_script.write_text("export TEST_VERTEX_VAR=hello_vertex\n")

    runner = CliRunner()

    mock_proc_vertex = MagicMock()
    mock_proc_vertex.returncode = 0
    mock_proc_vertex.stdout = "TEST_VERTEX_VAR=hello_vertex\nOTHER_VAR=123\n"

    mock_proc_bridge = MagicMock()
    mock_proc_bridge.returncode = 0

    def fake_subprocess_run(cmd, *args, **kwargs):
        if isinstance(cmd, list) and len(cmd) >= 3 and cmd[0] == "/bin/bash":
            assert "shell" not in kwargs or not kwargs["shell"]
            assert cmd == ["/bin/bash", "-c", 'source "$1" && env', "_", str(vertex_env_script)]
            return mock_proc_vertex
        else:
            return mock_proc_bridge

    with (
        patch("os.path.exists", return_value=True),
        patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(vertex_env_script)),
        patch("subprocess.run", side_effect=fake_subprocess_run) as mock_run,
    ):
        result = runner.invoke(bridge)
        assert result.exit_code == 0
        assert "Launching AGY bridge" in result.output

        # Verify second subprocess call received the parsed env
        assert mock_run.call_count == 2
        bridge_call_kwargs = mock_run.call_args_list[1].kwargs
        assert "env" in bridge_call_kwargs
        assert bridge_call_kwargs["env"].get("TEST_VERTEX_VAR") == "hello_vertex"
        assert bridge_call_kwargs["env"].get("OTHER_VAR") == "123"
