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

"""Tests for terminal output color-coding in run command."""

from unittest.mock import patch

from google.agents.cli.run.cmd_run import _print_author_tag, _print_sse_part


def test_print_author_tag_color():
    with patch("click.secho") as mock_secho:
        updated_author = _print_author_tag("agent_bob", None)
        assert updated_author == "agent_bob"
        mock_secho.assert_called_once_with("[agent_bob]: ", fg="green", bold=True, nl=False)


def test_print_sse_part_colors():
    # Test fileData tag (cyan)
    with patch("click.secho") as mock_secho:
        _print_sse_part({"fileData": {"fileUri": "gs://bucket/sample.png"}}, [])
        mock_secho.assert_called_once_with("\n[file: gs://bucket/sample.png]", fg="cyan", nl=False)

    # Test functionCall tag (blue, bold)
    with patch("click.secho") as mock_secho:
        _print_sse_part({"functionCall": {"name": "search", "args": {"q": "python"}}}, [])
        mock_secho.assert_called_once_with(
            '\n[tool_call: search({"q": "python"})]', fg="blue", bold=True, nl=False
        )

    # Test functionResponse tag (magenta)
    with patch("click.secho") as mock_secho:
        _print_sse_part({"functionResponse": {"name": "search", "response": {"result": "ok"}}}, [])
        mock_secho.assert_called_once_with(
            '\n[tool_response: search -> {"result": "ok"}]', fg="magenta", nl=False
        )
