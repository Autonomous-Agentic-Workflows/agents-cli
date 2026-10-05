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

"""Tests for `agy` command helpers."""

import tempfile
from pathlib import Path

from google.agents.cli.dev.cmd_agy import _load_env_script


def test_load_env_script_parses_variables():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".sh") as tmp:
        tmp.write(
            "# Comment line\n"
            "export VERTEXAI_LOCATION=us-central1\n"
            "GOOGLE_CLOUD_PROJECT=\"my-project-123\"\n"
            "   export   API_KEY='secret_key_abc'  \n"
            "\n"
        )
        tmp_path = tmp.name

    try:
        env = {}
        _load_env_script(tmp_path, env)
        assert env.get("VERTEXAI_LOCATION") == "us-central1"
        assert env.get("GOOGLE_CLOUD_PROJECT") == "my-project-123"
        assert env.get("API_KEY") == "secret_key_abc"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_load_env_script_nonexistent_file():
    env = {}
    _load_env_script("/nonexistent/file/path.sh", env)
    assert env == {}
