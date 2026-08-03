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


def test_redact_cmd_case_insensitive():
    # Case insensitivity for options and env vars
    args_1 = ["python", "-m", "main", "--API-KEY", "AIzaSyKey123"]
    assert redact_cmd(args_1) == "python -m main --API-KEY '[REDACTED]'"

    args_2 = ["env", "Gemini_Api_Key=AIzaSyKey123", "python"]
    assert redact_cmd(args_2) == "env 'Gemini_Api_Key=[REDACTED]' python"


def test_redact_cmd_short_terms_boundaries():
    # Exact component boundaries for 'pat' and 'pass'
    assert redact_cmd(["gcloud", "--path", "/my/path"]) == "gcloud --path /my/path"
    assert redact_cmd(["gcloud", "--compat", "true"]) == "gcloud --compat true"
    assert redact_cmd(["gcloud", "--pattern", "regex"]) == "gcloud --pattern regex"
    assert redact_cmd(["gcloud", "--template", "tmpl"]) == "gcloud --template tmpl"
    assert redact_cmd(["gcloud", "--key_id", "key123"]) == "gcloud --key_id key123"
    assert redact_cmd(["gcloud", "--patch", "v1"]) == "gcloud --patch v1"
    assert redact_cmd(["gcloud", "--passenger", "true"]) == "gcloud --passenger true"
    assert redact_cmd(["gcloud", "bypass"]) == "gcloud bypass"

    # Positive matches
    assert redact_cmd(["gcloud", "--my-pat", "123"]) == "gcloud --my-pat '[REDACTED]'"
    assert redact_cmd(["gcloud", "--db-pass", "123"]) == "gcloud --db-pass '[REDACTED]'"


def test_redact_cmd_comma_separated_lists():
    # Comma-separated option lists
    args = ["gcloud", "deploy", "--options=foo=bar,api_key=secret_123,baz=qux"]
    assert (
        redact_cmd(args)
        == "gcloud deploy '--options=foo=bar,api_key=[REDACTED],baz=qux'"
    )

    args_2 = ["gcloud", "deploy", "foo=bar,pat=abc"]
    assert redact_cmd(args_2) == "gcloud deploy 'foo=bar,pat=[REDACTED]'"
