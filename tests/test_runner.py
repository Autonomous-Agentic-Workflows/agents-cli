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


def test_redact_cmd_case_insensitive_and_dynamic_keys():
    # Custom API keys, tokens, and passwords
    args = ["my-cli", "--hf-token", "hf_secret123", "--db-password", "supersecurepassword", "--some-secret", "abc"]
    assert redact_cmd(args) == "my-cli --hf-token '[REDACTED]' --db-password '[REDACTED]' --some-secret '[REDACTED]'"

    # Equals format
    args_eq = ["my-cli", "--HF_TOKEN=hf_secret123", "--DB-PASSWORD=supersecurepassword", "--SOME_SECRET=abc"]
    assert redact_cmd(args_eq) == "my-cli '--HF_TOKEN=[REDACTED]' '--DB-PASSWORD=[REDACTED]' '--SOME_SECRET=[REDACTED]'"


def test_redact_cmd_ignored_keys():
    # Ignored keywords like "path", "compat", "pattern", "template", "key_id" should not be redacted
    args = ["my-cli", "--token-path", "/usr/bin/token", "--compat-secret", "val", "--regex-pattern", "some-pattern", "--secret-template", "tpl", "--api-key-id", "123"]
    assert redact_cmd(args) == "my-cli --token-path /usr/bin/token --compat-secret val --regex-pattern some-pattern --secret-template tpl --api-key-id 123"


def test_redact_cmd_inline_comma_separated():
    # Options that are comma-separated and contain sensitive sub-keys
    args = ["my-cli", "--options", "arg1=val1,api_key=secret_123,arg2=val2,password=secret_pass"]
    assert redact_cmd(args) == "my-cli --options 'arg1=val1,api_key=[REDACTED],arg2=val2,password=[REDACTED]'"

    # Option containing no keys but containing a comma-separated list
    args_plain = ["my-cli", "--options", "a,b,c"]
    assert redact_cmd(args_plain) == "my-cli --options a,b,c"
