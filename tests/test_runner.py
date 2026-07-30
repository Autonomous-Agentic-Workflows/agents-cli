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


def test_redact_cmd_security_enhancements():
    # Case insensitivity
    args_case = ["python", "-m", "main", "--API-Key", "AIzaSyKey123"]
    assert redact_cmd(args_case) == "python -m main --API-Key '[REDACTED]'"

    # Short terms boundary match (snake_case/kebab-case)
    args_pat = ["env", "MY_GITHUB_PAT=12345", "python"]
    assert redact_cmd(args_pat) == "env 'MY_GITHUB_PAT=[REDACTED]' python"

    args_pass = ["env", "ADMIN_PASSWORD=secret", "python"]
    assert redact_cmd(args_pass) == "env 'ADMIN_PASSWORD=[REDACTED]' python"

    args_pass_short = ["env", "MY_PASS=123", "python"]
    assert redact_cmd(args_pass_short) == "env 'MY_PASS=[REDACTED]' python"

    # Avoid false positives for short terms containing 'pat' or 'pass' as substring
    args_false_pos = [
        "env",
        "PATH=/bin",
        "COMPAT_MODE=1",
        "PATTERN=abc",
        "TEMPLATE=xyz",
        "KEY_ID=1",
        "PATCH_LEVEL=2",
        "PASSENGER=true",
        "python",
    ]
    assert (
        redact_cmd(args_false_pos)
        == "env PATH=/bin COMPAT_MODE=1 PATTERN=abc TEMPLATE=xyz KEY_ID=1 PATCH_LEVEL=2 PASSENGER=true python"
    )

    # Comma-separated list option redaction
    args_comma = [
        "gcloud",
        "--update-env-vars=GEMINI_API_KEY=123,ANOTHER_VAR=abc,DB_PASS=xyz",
        "deploy",
    ]
    assert (
        redact_cmd(args_comma)
        == "gcloud '--update-env-vars=GEMINI_API_KEY=[REDACTED],ANOTHER_VAR=abc,DB_PASS=[REDACTED]' deploy"
    )
