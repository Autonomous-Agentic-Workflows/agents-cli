import os
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import agy, bridge


def test_agy_bridge_sources_vertex_env_safely(tmp_path):
    runner = CliRunner()

    # Create dummy files for AGY_BRIDGE, AGY_HARNESS, and VERTEX_ENV
    bridge_script = tmp_path / "bridge.py"
    bridge_script.write_text("print('hello')")

    harness_bin = tmp_path / "localharness"
    harness_bin.write_text("echo harness")

    vertex_env = tmp_path / "setup_vertex.sh"
    vertex_env.write_text("export TEST_VERTEX_VAR=custom_value\n")

    with patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_script)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_bin)), \
         patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(vertex_env)), \
         patch("subprocess.run") as mock_run:

        # Mock the subprocess.run call for sourcing VERTEX_ENV
        mock_sourced_res = MagicMock()
        mock_sourced_res.stdout = "TEST_VERTEX_VAR=custom_value\nOTHER_VAR=123"

        # Mock the second subprocess.run for launching AGY_PY
        mock_py_res = MagicMock()

        mock_run.side_effect = [mock_sourced_res, mock_py_res]

        result = runner.invoke(agy, ["bridge"])

        assert result.exit_code == 0
        assert mock_run.call_count == 2

        # Verify first call uses parameterized bash without shell=True
        first_call_args, first_call_kwargs = mock_run.call_args_list[0]
        assert first_call_args[0] == ["/bin/bash", "-c", 'source "$1" && env', "_", str(vertex_env)]
        assert "shell" not in first_call_kwargs or first_call_kwargs["shell"] is False

        # Verify environment passed to second call includes sourced variable
        second_call_args, second_call_kwargs = mock_run.call_args_list[1]
        passed_env = second_call_kwargs.get("env", {})
        assert passed_env.get("TEST_VERTEX_VAR") == "custom_value"
        assert passed_env.get("OTHER_VAR") == "123"
