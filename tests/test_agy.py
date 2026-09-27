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

"""Tests for AGY CLI commands and helper functions."""

from google.agents.cli.dev.cmd_agy import _load_vertex_env


def test_load_vertex_env(tmp_path):
    env_file = tmp_path / "setup_env.sh"
    env_file.write_text(
        "# Comment line\n"
        "export GOOGLE_CLOUD_PROJECT='my-test-project'\n"
        "export VERTEXAI_LOCATION=\"us-east1\"\n"
        "OTHER_VAR=value_without_export\n"
        "\n"
        "  # Ignored comment\n"
    )

    env = {}
    _load_vertex_env(env, str(env_file))

    assert env.get("GOOGLE_CLOUD_PROJECT") == "my-test-project"
    assert env.get("VERTEXAI_LOCATION") == "us-east1"
    assert env.get("OTHER_VAR") == "value_without_export"
