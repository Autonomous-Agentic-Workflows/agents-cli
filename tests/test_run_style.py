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

"""Tests for terminal run command output visual styles."""

from unittest.mock import patch
from a2a.types import Part, TextPart, FilePart, FileWithUri
from google.agents.cli.run.cmd_run import (
    _print_author_tag,
    _print_sse_part,
    _print_a2a_part,
)


@patch("google.agents.cli.run.cmd_run.click")
def test_print_author_tag(mock_click):
    # Test first author tag print (no last author)
    result = _print_author_tag("agent", None)
    assert result == "agent"
    mock_click.secho.assert_called_once_with(
        "[agent]: ", fg="green", bold=True, nl=False
    )
    mock_click.echo.assert_not_called()

    mock_click.reset_mock()

    # Test same author tag print (should not reprint)
    result2 = _print_author_tag("agent", "agent")
    assert result2 == "agent"
    mock_click.secho.assert_not_called()
    mock_click.echo.assert_not_called()

    # Test changing author tag print (should print newline first)
    result3 = _print_author_tag("user", "agent")
    assert result3 == "user"
    mock_click.echo.assert_called_once()
    mock_click.secho.assert_called_once_with(
        "[user]: ", fg="green", bold=True, nl=False
    )


@patch("google.agents.cli.run.cmd_run.click")
def test_print_sse_part_text(mock_click):
    artifacts = []
    _print_sse_part({"text": "Hello world!"}, artifacts)
    mock_click.echo.assert_called_once_with("Hello world!", nl=False)
    mock_click.secho.assert_not_called()


@patch("google.agents.cli.run.cmd_run.click")
def test_print_sse_part_file_uri(mock_click):
    artifacts = []
    _print_sse_part({"fileData": {"fileUri": "gs://bucket/file.png"}}, artifacts)
    mock_click.secho.assert_called_once_with(
        "\n[file: gs://bucket/file.png]", fg="cyan", nl=False
    )
    mock_click.echo.assert_not_called()


@patch("google.agents.cli.run.cmd_run.click")
def test_print_sse_part_function_call(mock_click):
    artifacts = []
    _print_sse_part(
        {"functionCall": {"name": "get_weather", "args": {"location": "SF"}}}, artifacts
    )
    mock_click.secho.assert_called_once_with(
        '\n[tool_call: get_weather({"location": "SF"})]', fg="blue", bold=True, nl=False
    )
    mock_click.echo.assert_not_called()


@patch("google.agents.cli.run.cmd_run.click")
def test_print_sse_part_function_response(mock_click):
    artifacts = []
    _print_sse_part(
        {"functionResponse": {"name": "get_weather", "response": {"temp": 72}}},
        artifacts,
    )
    mock_click.secho.assert_called_once_with(
        '\n[tool_response: get_weather -> {"temp": 72}]', fg="magenta", nl=False
    )
    mock_click.echo.assert_not_called()


@patch("google.agents.cli.run.cmd_run.click")
def test_print_a2a_part_text(mock_click):
    artifacts = []
    part = Part(TextPart(text="Hello from A2A!"))
    _print_a2a_part(part, artifacts)
    mock_click.echo.assert_called_once_with("Hello from A2A!", nl=False)
    mock_click.secho.assert_not_called()


@patch("google.agents.cli.run.cmd_run.click")
def test_print_a2a_part_file_uri(mock_click):
    artifacts = []
    file_with_uri = FileWithUri(uri="https://example.com/image.png")
    part = Part(FilePart(file=file_with_uri))
    _print_a2a_part(part, artifacts)
    mock_click.secho.assert_called_once_with(
        "\n[file: https://example.com/image.png]", fg="cyan", nl=False
    )
    mock_click.echo.assert_not_called()
