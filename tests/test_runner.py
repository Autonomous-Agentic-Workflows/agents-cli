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

"""Tests for subprocess helpers/redactions."""

from google.agents.cli._runner import redact_cmd


def test_redact_cmd_github_pat():
    # Option flag with separate value arg
    args = ["gcloud", "--github-pat", "secret_token_123", "deploy"]
    assert redact_cmd(args) == "gcloud --github-pat '[REDACTED]' deploy"

    # Option flag with key=value format
    args = ["gcloud", "--github-pat=secret_token_123", "deploy"]
    assert redact_cmd(args) == "gcloud '--github-pat=[REDACTED]' deploy"


def test_redact_cmd_api_key_options():
    # Option flags with separate value arg
    args_1 = ["python", "-m", "main", "--api-key", "AIzaSyKey123"]
    assert redact_cmd(args_1) == "python -m main --api-key '[REDACTED]'"

    args_2 = ["python", "-m", "main", "--api_key", "AIzaSyKey123"]
    assert redact_cmd(args_2) == "python -m main --api_key '[REDACTED]'"

    # Option flags with key=value format
    args_3 = ["python", "-m", "main", "--api-key=AIzaSyKey123"]
    assert redact_cmd(args_3) == "python -m main '--api-key=[REDACTED]'"

    args_4 = ["python", "-m", "main", "--api_key=AIzaSyKey123"]
    assert redact_cmd(args_4) == "python -m main '--api_key=[REDACTED]'"


def test_redact_cmd_env_vars():
    # Exact key=value env vars
    args_1 = ["env", "GEMINI_API_KEY=AIzaSyKey123", "python"]
    assert redact_cmd(args_1) == "env 'GEMINI_API_KEY=[REDACTED]' python"

    args_2 = ["env", "GOOGLE_API_KEY=AIzaSyKey123", "python"]
    assert redact_cmd(args_2) == "env 'GOOGLE_API_KEY=[REDACTED]' python"

    args_3 = ["env", "GITHUB_PAT=pat_123", "python"]
    assert redact_cmd(args_3) == "env 'GITHUB_PAT=[REDACTED]' python"

    # Env var containing name but with value inside some other format
    args_4 = ["env", "SOME_VAR=my_GEMINI_API_KEY_value", "python"]
    assert redact_cmd(args_4) == "env '[REDACTED]' python"


def test_redact_cmd_no_secrets():
    # Normal commands
    args = ["git", "commit", "-m", "regular commit message"]
    assert redact_cmd(args) == "git commit -m 'regular commit message'"


def test_redact_cmd_case_insensitivity():
    # Verify case-insensitive matching for various sensitive keys
    args = ["env", "gemini_api_key=AIzaSyKey123", "python"]
    assert redact_cmd(args) == "env 'gemini_api_key=[REDACTED]' python"

    args2 = ["env", "GitHub_PAT=pat_123", "python"]
    assert redact_cmd(args2) == "env 'GitHub_PAT=[REDACTED]' python"

    args3 = ["python", "-m", "main", "--API_KEY", "AIzaSyKey123"]
    assert redact_cmd(args3) == "python -m main --API_KEY '[REDACTED]'"


def test_redact_cmd_comma_separated():
    # Comma-separated options / environment variable redactions
    args = ["--options", "debug=true,api_key=123,verbose=false"]
    assert redact_cmd(args) == "--options 'debug=true,api_key=[REDACTED],verbose=false'"

    args2 = ["--options", "debug=true,gemini_api_key:123,verbose=false"]
    assert redact_cmd(args2) == "--options 'debug=true,gemini_api_key:[REDACTED],verbose=false'"


def test_redact_cmd_component_boundaries():
    # Ensure short terms like pat and pass are matched on boundary components
    # to avoid false positives (e.g., path, compat, compass, compat-mode, etc.)
    args1 = ["--path", "/usr/bin"]
    assert redact_cmd(args1) == "--path /usr/bin"

    args2 = ["--compat-mode", "legacy"]
    assert redact_cmd(args2) == "--compat-mode legacy"

    args3 = ["--my-pat-value", "secret"]
    assert redact_cmd(args3) == "--my-pat-value '[REDACTED]'"

    args4 = ["--my-pat", "secret"]
    assert redact_cmd(args4) == "--my-pat '[REDACTED]'"

    args5 = ["--my-pass", "secret"]
    assert redact_cmd(args5) == "--my-pass '[REDACTED]'"

    args6 = ["--compass", "north"]
    assert redact_cmd(args6) == "--compass north"
