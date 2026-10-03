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

"""Tests for google.agents.cli.dev.cmd_agy module."""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from google.agents.cli.dev.cmd_agy import agy


def test_agy_bridge_parses_vertex_env(tmp_path):
    vertex_env_file = tmp_path / "setup_vertex_env.sh"
    vertex_env_file.write_text(
        "# Comment line\n"
        "export CUSTOM_VERTEX_KEY=secret_value_123\n"
        "ANOTHER_KEY=\"another_value\"\n",
        encoding="utf-8",
    )

    runner = CliRunner()

    with (
        patch("os.path.exists", return_value=True),
        patch("google.agents.cli.dev.cmd_agy.VERTEX_ENV", str(vertex_env_file)),
        patch("subprocess.run") as mock_run,
    ):
        result = runner.invoke(agy, ["bridge"])

        assert result.exit_code == 0
        assert mock_run.called
        # Verify shell=True is not used
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs.get("shell") is not True

        env_passed = call_kwargs.get("env", {})
        assert env_passed.get("CUSTOM_VERTEX_KEY") == "secret_value_123"
        assert env_passed.get("ANOTHER_KEY") == "another_value"
