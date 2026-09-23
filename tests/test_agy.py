from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import os

from google.agents.cli.dev.cmd_agy import agy, bridge


def test_agy_bridge_parses_vertex_env(tmp_path):
    env_script = tmp_path / "setup_vertex_env.sh"
    env_script.write_text(
        "# Comment line\n"
        "export CUSTOM_VERTEX_KEY=secret_val_123\n"
        "ANOTHER_VAR='quoted_value'\n"
    )

    runner = CliRunner()
    with patch("os.path.exists") as mock_exists, \
         patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_script)), \
         patch("subprocess.run") as mock_subprocess_run:

        def exists_side_effect(path):
            if path in (str(env_script), "/mock/bridge.py", "/mock/localharness"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        with patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", "/mock/bridge.py"), \
             patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", "/mock/localharness"):
            result = runner.invoke(agy, ["bridge"])

            assert result.exit_code == 0
            mock_subprocess_run.assert_called_once()
            called_args, called_kwargs = mock_subprocess_run.call_args
            passed_env = called_kwargs.get("env", {})
            assert passed_env.get("CUSTOM_VERTEX_KEY") == "secret_val_123"
            assert passed_env.get("ANOTHER_VAR") == "quoted_value"
            # Verify shell=True was NOT used
            assert called_kwargs.get("shell") is not True
