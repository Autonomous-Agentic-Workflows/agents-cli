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

import shlex
from google.agents.cli._runner import redact_cmd


def test_redact_cmd_github_pat():
    args = ["git", "clone", "--github-pat", "ghp_1234567890abcdef", "https://github.com/repo"]
    redacted = redact_cmd(args)
    assert "[REDACTED]" in redacted
    assert "ghp_1234567890" not in redacted


def test_redact_cmd_gemini_api_key():
    args = ["my-agent-cli", "run", "GEMINI_API_KEY=AIzaSySecretKey", "--verbose"]
    redacted = redact_cmd(args)
    assert "[REDACTED]" in redacted
    assert "AIzaSySecretKey" not in redacted


def test_redact_cmd_google_api_key():
    args = ["my-agent-cli", "run", "GOOGLE_API_KEY=another_secret_key"]
    redacted = redact_cmd(args)
    assert "[REDACTED]" in redacted
    assert "another_secret_key" not in redacted


def test_redact_cmd_google_genai_api_key():
    args = ["my-agent-cli", "run", "GOOGLE_GENAI_API_KEY=genai_secret_key"]
    redacted = redact_cmd(args)
    assert "[REDACTED]" in redacted
    assert "genai_secret_key" not in redacted


def test_redact_cmd_api_key_options():
    options = ["--api-key", "--api_key", "--access-token", "--access_token"]
    for option in options:
        args = ["my-agent-cli", "deploy", option, "my-super-secret-token"]
        redacted = redact_cmd(args)
        assert "[REDACTED]" in redacted
        assert "my-super-secret-token" not in redacted


def test_redact_cmd_api_key_equals_options():
    options = ["--api-key", "--api_key", "--access-token", "--access_token"]
    for option in options:
        args = ["my-agent-cli", "deploy", f"{option}=my-super-secret-token"]
        redacted = redact_cmd(args)
        assert f"{option}=[REDACTED]" in redacted
        assert "my-super-secret-token" not in redacted


def test_redact_cmd_no_secrets():
    args = ["agents-cli", "scaffold", "my_new_agent", "--region", "us-central1"]
    redacted = redact_cmd(args)
    assert redacted == shlex.join(args)
