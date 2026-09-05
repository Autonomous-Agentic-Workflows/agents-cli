"""Unit tests for the agy command group."""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import pytest

from google.agents.cli.dev.cmd_agy import agy, bridge


def test_agy_bridge_parses_vertex_env(tmp_path, monkeypatch):
    script_file = tmp_path / "setup_vertex_env.sh"
    script_file.write_text(
        "# Test script\n"
        "export TEST_VAR=hello_world\n"
        "QUOTED_VAR=\"test_value\"\n"
        "SINGLE_QUOTED='single_value'\n"
        "  # comment line  \n"
        "INVALID_LINE\n"
    )

    bridge_file = tmp_path / "bridge.py"
    bridge_file.write_text("# dummy bridge")

    harness_file = tmp_path / "localharness"
    harness_file.write_text("# dummy harness")

    monkeypatch.setattr("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(script_file))
    monkeypatch.setattr("google.agents.cli.dev.cmd_agy.AGY_BRIDGE", str(bridge_file))
    monkeypatch.setattr("google.agents.cli.dev.cmd_agy.AGY_HARNESS", str(harness_file))

    runner = CliRunner()
    with patch("subprocess.run") as mock_run:
        result = runner.invoke(agy, ["bridge"])
        assert result.exit_code == 0
        assert mock_run.called
        call_args, call_kwargs = mock_run.call_args
        env_passed = call_kwargs.get("env", {})
        assert env_passed.get("TEST_VAR") == "hello_world"
        assert env_passed.get("QUOTED_VAR") == "test_value"
        assert env_passed.get("SINGLE_QUOTED") == "single_value"
