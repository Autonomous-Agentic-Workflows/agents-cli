import os
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from google.agents.cli.dev.cmd_agy import agy


def test_agy_bridge_vertex_env_sourcing(tmp_path):
    env_script = tmp_path / "setup_vertex.sh"
    env_script.write_text("export TEST_VERTEX_VAR=hello_sentinel\n")

    bridge_script = tmp_path / "bridge.py"
    bridge_script.write_text("print('bridge running')\n")

    harness_file = tmp_path / "localharness"
    harness_file.write_text("harness")

    runner = CliRunner()

    with patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_script)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_script)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_file)), \
         patch("subprocess.run") as mock_run:

        # Mock the bash subprocess run for sourcing VERTEX_ENV
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "TEST_VERTEX_VAR=hello_sentinel\n"
        mock_run.side_effect = [mock_proc, MagicMock(returncode=0)]

        result = runner.invoke(agy, ["bridge"])

        assert result.exit_code == 0
        assert mock_run.call_count >= 1

        # Check that the first subprocess call was the safe parameterized bash execution
        first_call_args = mock_run.call_args_list[0][0][0]
        assert first_call_args == ["/bin/bash", "-c", 'source "$1" && env', "_", str(env_script)]
