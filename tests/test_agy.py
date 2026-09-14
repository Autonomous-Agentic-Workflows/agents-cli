from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from google.agents.cli.dev.cmd_agy import bridge, agy


def test_agy_group():
    runner = CliRunner()
    result = runner.invoke(agy, ["--help"])
    assert result.exit_code == 0
    assert "Commands for interacting with the Google Antigravity SDK" in result.output


def test_bridge_parses_vertex_env_without_shell_true(tmp_path):
    bridge_path = tmp_path / "bridge.py"
    bridge_path.write_text("# dummy bridge")
    harness_path = tmp_path / "localharness"
    harness_path.write_text("# dummy harness")
    vertex_env_path = tmp_path / "setup_vertex.sh"
    vertex_env_path.write_text(
        '# Comment\nexport CUSTOM_VAR="hello_world"\nANOTHER_VAR=123\n'
    )

    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_path)), \
         patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_path)), \
         patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(vertex_env_path)), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(bridge)
        assert result.exit_code == 0

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        # Ensure shell=True was NOT passed
        assert kwargs.get("shell") is not True
        env_passed = kwargs.get("env", {})
        assert env_passed.get("CUSTOM_VAR") == "hello_world"
        assert env_passed.get("ANOTHER_VAR") == "123"
