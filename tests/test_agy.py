"""Tests for cmd_agy module."""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from google.agents.cli.dev import cmd_agy


def test_agy_bridge_sources_vertex_env_without_shell_true(tmp_path):
    runner = CliRunner()
    fake_env_script = tmp_path / "setup_vertex.sh"
    fake_env_script.write_text("export TEST_VERTEX_VAR=hello_vertex\n")

    fake_bridge = tmp_path / "bridge.py"
    fake_bridge.write_text("print('bridge')\n")
    fake_harness = tmp_path / "localharness"
    fake_harness.write_text("harness\n")

    with patch.object(cmd_agy, "VERTEX_ENV", str(fake_env_script)), \
         patch.object(cmd_agy, "AGY_BRIDGE", str(fake_bridge)), \
         patch.object(cmd_agy, "AGY_HARNESS", str(fake_harness)), \
         patch("subprocess.run") as mock_run:

        mock_res = MagicMock()
        mock_res.stdout = "TEST_VERTEX_VAR=hello_vertex\n"
        mock_run.return_value = mock_res

        result = runner.invoke(cmd_agy.bridge)

        assert result.exit_code == 0
        # Verify subprocess.run calls do not use shell=True
        for call_args, call_kwargs in mock_run.call_args_list:
            assert call_kwargs.get("shell") is not True
