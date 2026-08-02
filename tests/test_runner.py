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


def test_redact_cmd_dynamic_and_case_insensitive():
    # Test case-insensitive options and env vars
    assert redact_cmd(["gcloud", "--API-KEY", "secret123"]) == "gcloud --API-KEY '[REDACTED]'"
    assert redact_cmd(["env", "gemini_api_key=secret123"]) == "env 'gemini_api_key=[REDACTED]'"

    # Test comma-separated option lists
    assert redact_cmd(["deploy", "--options=api_key=secret,token=foo,other=bar"]) == "deploy '--options=api_key=[REDACTED],token=[REDACTED],other=bar'"

    # Test exact component boundary checks for short terms like 'pat' and 'pass'
    assert redact_cmd(["deploy", "--github-pat", "secret_pat"]) == "deploy --github-pat '[REDACTED]'"
    assert redact_cmd(["deploy", "--github_pat=secret_pat"]) == "deploy '--github_pat=[REDACTED]'"
    assert redact_cmd(["deploy", "--pass-phrase", "secret_pass"]) == "deploy --pass-phrase '[REDACTED]'"

    # Test prevention of false positives (must not redact path, compat, pattern, template, key_id, patch, passenger, bypass)
    assert redact_cmd(["python", "script.py", "--path", "/my/path"]) == "python script.py --path /my/path"
    assert redact_cmd(["python", "script.py", "--compat=true"]) == "python script.py --compat=true"
    assert redact_cmd(["python", "script.py", "--pattern=abc"]) == "python script.py --pattern=abc"
    assert redact_cmd(["python", "script.py", "--template=xyz"]) == "python script.py --template=xyz"
    assert redact_cmd(["python", "script.py", "--key_id=123"]) == "python script.py --key_id=123"
    assert redact_cmd(["python", "script.py", "--patch=true"]) == "python script.py --patch=true"
    assert redact_cmd(["python", "script.py", "--passenger=yes"]) == "python script.py --passenger=yes"
    assert redact_cmd(["python", "script.py", "--bypass=true"]) == "python script.py --bypass=true"
