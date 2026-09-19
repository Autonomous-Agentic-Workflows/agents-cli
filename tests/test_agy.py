"""Tests for agy command module."""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import agy


def test_agy_bridge_parses_vertex_env(tmp_path):
    """Test that agy bridge safely parses VERTEX_ENV file without shell=True."""
    env_file = tmp_path / "setup_vertex.sh"
    env_file.write_text(
        "# Comment line\n"
        "export TEST_VAR_ONE=hello\n"
        "TEST_VAR_TWO='world'\n"
        "TEST_VAR_THREE=\"quoted_val\"\n"
    )

    runner = CliRunner()

    with patch("os.path.exists") as mock_exists, patch("subprocess.run") as mock_subproc:
        # Return True for AGY_BRIDGE, AGY_HARNESS, and env_file
        mock_exists.side_effect = lambda path: True

        with patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(env_file)):
            result = runner.invoke(agy, ["bridge"])

        assert result.exit_code == 0
        assert mock_subproc.called

        # Ensure shell=True was never passed in any subprocess invocation
        for call_args in mock_subproc.call_args_list:
            kwargs = call_args.kwargs
            assert not kwargs.get("shell", False)

        # Inspect the env dictionary passed to subprocess.run([AGY_PY, AGY_BRIDGE])
        passed_env = mock_subproc.call_args.kwargs.get("env", {})
        assert passed_env.get("TEST_VAR_ONE") == "hello"
        assert passed_env.get("TEST_VAR_TWO") == "world"
        assert passed_env.get("TEST_VAR_THREE") == "quoted_val"
