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


def test_redact_cmd_case_insensitive_and_extended():
    # Case-insensitivity for options
    args_1 = ["python", "-m", "main", "--API-KEY", "AIzaSyKey123"]
    assert redact_cmd(args_1) == "python -m main --API-KEY '[REDACTED]'"

    args_2 = ["python", "-m", "main", "--Api_Key=AIzaSyKey123"]
    assert redact_cmd(args_2) == "python -m main '--Api_Key=[REDACTED]'"

    # Extended options (e.g. password, token, secret)
    args_3 = ["deploy", "--password", "supersecretpwd"]
    assert redact_cmd(args_3) == "deploy --password '[REDACTED]'"

    args_4 = ["deploy", "--access-token=my-access-token-123"]
    assert redact_cmd(args_4) == "deploy '--access-token=[REDACTED]'"

    # Case-insensitive env vars (e.g. lowercase)
    args_5 = ["env", "gemini_api_key=AIzaSyKey123", "python"]
    assert redact_cmd(args_5) == "env 'gemini_api_key=[REDACTED]' python"

    args_6 = ["env", "db_password=mypassword", "python"]
    assert redact_cmd(args_6) == "env 'db_password=[REDACTED]' python"


def test_redact_cmd_generic_secrets_and_comma_separated():
    # Generic secret env vars (OpenAI, Anthropic, Bearer Token, Private Key)
    args_1 = ["env", "OPENAI_API_KEY=sk-12345", "python"]
    assert redact_cmd(args_1) == "env 'OPENAI_API_KEY=[REDACTED]' python"

    args_2 = ["env", "BEARER_TOKEN=token123", "python"]
    assert redact_cmd(args_2) == "env 'BEARER_TOKEN=[REDACTED]' python"

    args_3 = ["env", "PRIVATE_KEY=pk_secret", "python"]
    assert redact_cmd(args_3) == "env 'PRIVATE_KEY=[REDACTED]' python"

    # New options flags
    args_4 = ["deploy", "--bearer-token", "bearer123"]
    assert redact_cmd(args_4) == "deploy --bearer-token '[REDACTED]'"

    args_5 = ["deploy", "--private-key=pk_123"]
    assert redact_cmd(args_5) == "deploy '--private-key=[REDACTED]'"

    # Comma-separated env vars
    args_6 = ["deploy", "--update-env-vars", "FOO=bar,OPENAI_API_KEY=sk-123,BAZ=qux"]
    assert (
        redact_cmd(args_6)
        == "deploy --update-env-vars 'FOO=bar,OPENAI_API_KEY=[REDACTED],BAZ=qux'"
    )
