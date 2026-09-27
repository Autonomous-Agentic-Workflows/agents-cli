from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import bridge


def test_bridge_vertex_env_parsing(tmp_path):
    vertex_env_file = tmp_path / "setup_vertex.sh"
    vertex_env_file.write_text("export TEST_VAR=hello_world\nMY_FOO='bar'\n# comment\n")

    fake_py = tmp_path / "python"
    fake_py.write_text("#!/bin/sh\n")
    fake_harness = tmp_path / "harness"
    fake_harness.write_text("")
    fake_bridge = tmp_path / "bridge.py"
    fake_bridge.write_text("")

    with (
        patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(vertex_env_file)),
        patch("google.agents.cli.dev.cmd_agy.AGY_PY", str(fake_py)),
        patch("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(fake_harness)),
        patch("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(fake_bridge)),
        patch("subprocess.run") as mock_run,
    ):
        runner = CliRunner()
        result = runner.invoke(bridge)

        assert result.exit_code == 0
        assert mock_run.called

        # Check that subprocess.run was called without shell=True
        call_args, call_kwargs = mock_run.call_args
        assert call_kwargs.get("shell") is not True
        passed_env = call_kwargs.get("env", {})
        assert passed_env.get("TEST_VAR") == "hello_world"
        assert passed_env.get("MY_FOO") == "bar"
