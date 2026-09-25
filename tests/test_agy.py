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

from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import google.agents.cli.dev.cmd_agy as cmd_agy


def test_agy_bridge_parses_vertex_env(tmp_path):
    """Verify VERTEX_ENV is parsed into env dictionary without shell=True."""
    env_script = tmp_path / "setup_env.sh"
    env_script.write_text(
        "# Comment line\n"
        "export VERTEX_PROJECT_ID=\"my-project-123\"\n"
        "CUSTOM_KEY=custom_value\n",
        encoding="utf-8",
    )

    runner = CliRunner()

    with (
        patch("os.path.exists") as mock_exists,
        patch("subprocess.run") as mock_sub_run,
        patch.object(cmd_agy, "VERTEX_ENV", str(env_script)),
    ):
        def exists_side_effect(path):
            if path in (cmd_agy.AGY_BRIDGE, cmd_agy.AGY_HARNESS):
                return True
            if path == str(env_script):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        result = runner.invoke(cmd_agy.bridge)

        assert result.exit_code == 0
        mock_sub_run.assert_called_once()

        # Ensure shell=True was NOT used
        kwargs = mock_sub_run.call_args.kwargs
        assert "shell" not in kwargs or kwargs["shell"] is False

        # Ensure env dict contains parsed variables
        passed_env = kwargs["env"]
        assert passed_env.get("VERTEX_PROJECT_ID") == "my-project-123"
        assert passed_env.get("CUSTOM_KEY") == "custom_value"
