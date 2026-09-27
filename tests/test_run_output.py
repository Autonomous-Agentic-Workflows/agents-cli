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

"""Unit tests for agents-cli run output formatting."""

from unittest.mock import patch

from a2a.types import FilePart, FileWithUri, Part

from google.agents.cli.run.cmd_run import (
    _print_a2a_part,
    _print_author_tag,
    _print_session_id,
    _print_sse_part,
)


def test_print_author_tag_color():
    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        # First author tag
        result = _print_author_tag("my_agent", None)
        assert result == "my_agent"
        mock_secho.assert_called_once_with("[my_agent]: ", fg="green", bold=True, nl=False)
        mock_echo.assert_not_called()

        # Same author tag -> no re-print
        mock_secho.reset_mock()
        result = _print_author_tag("my_agent", "my_agent")
        assert result == "my_agent"
        mock_secho.assert_not_called()


def test_print_sse_part_colors():
    artifacts = []

    # File part -> cyan
    with patch("click.secho") as mock_secho:
        _print_sse_part({"fileData": {"fileUri": "gs://bucket/file.png"}}, artifacts)
        mock_secho.assert_called_once_with("\n[file: gs://bucket/file.png]", fg="cyan", nl=False)

    # Tool call -> bold blue
    with patch("click.secho") as mock_secho:
        _print_sse_part(
            {"functionCall": {"name": "search", "args": {"q": "test"}}}, artifacts
        )
        mock_secho.assert_called_once_with(
            '\n[tool_call: search({"q": "test"})]', fg="blue", bold=True, nl=False
        )

    # Tool response -> magenta
    with patch("click.secho") as mock_secho:
        _print_sse_part(
            {"functionResponse": {"name": "search", "response": {"result": "ok"}}},
            artifacts,
        )
        mock_secho.assert_called_once_with(
            '\n[tool_response: search -> {"result": "ok"}]', fg="magenta", nl=False
        )


def test_print_a2a_part_file_color():
    artifacts = []
    part = Part(root=FilePart(file=FileWithUri(uri="https://example.com/file.pdf")))

    with patch("click.secho") as mock_secho:
        _print_a2a_part(part, artifacts)
        mock_secho.assert_called_once_with(
            "\n[file: https://example.com/file.pdf]", fg="cyan", nl=False
        )


def test_print_session_id_formatting():
    # None -> no output
    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        _print_session_id(None)
        mock_secho.assert_not_called()
        mock_echo.assert_not_called()

    # Session ID -> prints header dimmed and resume command in cyan
    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        _print_session_id("test-session-123")
        mock_echo.assert_called_once_with()
        assert mock_secho.call_count == 3
        mock_secho.assert_any_call("Session: test-session-123", dim=True)
        mock_secho.assert_any_call("  Resume with: ", dim=True, nl=False)
        mock_secho.assert_any_call(
            'agents-cli run "<message>" --session-id test-session-123', fg="cyan"
        )
