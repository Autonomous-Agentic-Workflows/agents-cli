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

"""Tests to verify UX color-coded formatting of different output parts."""

from unittest.mock import MagicMock, patch
import pytest

from google.agents.cli.run.cmd_run import (
    _print_author_tag,
    _print_sse_part,
    _print_a2a_part,
)
from a2a.types import Part, TextPart, FilePart, FileWithUri


@patch("click.secho")
@patch("click.echo")
def test_print_author_tag_color(mock_echo, mock_secho):
    # Test user author tag (should be yellow)
    _print_author_tag("user", None)
    mock_secho.assert_any_call("[user]: ", fg="yellow", bold=True, nl=False)

    # Test non-user (agent) author tag (should be green)
    _print_author_tag("agent_name", "user")
    mock_secho.assert_any_call("[agent_name]: ", fg="green", bold=True, nl=False)


@patch("click.secho")
@patch("click.echo")
def test_print_sse_part_file_color(mock_echo, mock_secho):
    artifacts = []
    part = {"fileData": {"fileUri": "gs://bucket/file.png"}}
    _print_sse_part(part, artifacts)
    mock_secho.assert_any_call("[file: gs://bucket/file.png]", fg="cyan", nl=False)


@patch("click.secho")
@patch("click.echo")
def test_print_sse_part_tool_call_color(mock_echo, mock_secho):
    artifacts = []
    part = {"functionCall": {"name": "get_weather", "args": {"location": "San Francisco"}}}
    _print_sse_part(part, artifacts)
    mock_secho.assert_any_call(
        '[tool_call: get_weather({"location": "San Francisco"})]',
        fg="blue",
        bold=True,
        nl=False,
    )


@patch("click.secho")
@patch("click.echo")
def test_print_sse_part_tool_response_color(mock_echo, mock_secho):
    artifacts = []
    part = {"functionResponse": {"name": "get_weather", "response": {"weather": "sunny"}}}
    _print_sse_part(part, artifacts)
    mock_secho.assert_any_call(
        '[tool_response: get_weather -> {"weather": "sunny"}]',
        fg="magenta",
        nl=False,
    )


@patch("click.secho")
@patch("click.echo")
def test_print_a2a_part_file_color(mock_echo, mock_secho):
    artifacts = []
    # Create an A2A FilePart with Uri
    uri_data = FileWithUri(uri="gs://my-bucket/report.pdf", mime_type="application/pdf")
    part = Part(root=FilePart(file=uri_data))
    _print_a2a_part(part, artifacts)
    mock_secho.assert_any_call("[file: gs://my-bucket/report.pdf]", fg="cyan", nl=False)
