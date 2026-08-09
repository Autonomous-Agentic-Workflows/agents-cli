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

"""Tests for terminal color-coded output formatting in cmd_run."""

from unittest import mock
import click
from a2a.types import Part, FilePart, FileWithUri

from google.agents.cli.run.cmd_run import (
    _print_author_tag,
    _print_sse_part,
    _print_a2a_part,
)


def test_print_author_tag_color():
    with mock.patch("click.secho") as mock_secho, mock.patch("click.echo") as mock_echo:
        # First call: printed in green
        res = _print_author_tag("my-agent", None)
        assert res == "my-agent"
        mock_secho.assert_called_once_with("[my-agent]: ", fg="green", nl=False)
        mock_echo.assert_not_called()

        mock_secho.reset_mock()
        mock_echo.reset_mock()

        # Second call with same author: should not print anything
        res2 = _print_author_tag("my-agent", "my-agent")
        assert res2 == "my-agent"
        mock_secho.assert_not_called()
        mock_echo.assert_not_called()

        # Third call with new author: prints newline via click.echo, then green tag via click.secho
        res3 = _print_author_tag("other-agent", "my-agent")
        assert res3 == "other-agent"
        mock_echo.assert_called_once_with()
        mock_secho.assert_called_once_with("[other-agent]: ", fg="green", nl=False)


def test_print_sse_part_text():
    artifacts = []
    with mock.patch("click.echo") as mock_echo:
        _print_sse_part({"text": "Hello world!"}, artifacts)
        mock_echo.assert_called_once_with("Hello world!", nl=False)


def test_print_sse_part_file_uri():
    artifacts = []
    with mock.patch("click.secho") as mock_secho:
        _print_sse_part({"fileData": {"fileUri": "gs://bucket/image.png"}}, artifacts)
        mock_secho.assert_called_once_with("\n[file: gs://bucket/image.png]", fg="cyan", nl=False)


def test_print_sse_part_tool_call():
    artifacts = []
    with mock.patch("click.secho") as mock_secho:
        part = {
            "functionCall": {
                "name": "calculate",
                "args": {"expression": "2 + 2"},
            }
        }
        _print_sse_part(part, artifacts)
        mock_secho.assert_called_once_with(
            '\n[tool_call: calculate({"expression": "2 + 2"})]',
            fg="blue",
            bold=True,
            nl=False,
        )


def test_print_sse_part_tool_response():
    artifacts = []
    with mock.patch("click.secho") as mock_secho:
        part = {
            "functionResponse": {
                "name": "calculate",
                "response": {"result": 4},
            }
        }
        _print_sse_part(part, artifacts)
        mock_secho.assert_called_once_with(
            '\n[tool_response: calculate -> {"result": 4}]',
            fg="magenta",
            nl=False,
        )


def test_print_a2a_part_file_uri():
    artifacts = []
    root = FilePart(file=FileWithUri(uri="gs://my-bucket/test.pdf"))
    part = Part(root=root)
    with mock.patch("click.secho") as mock_secho:
        _print_a2a_part(part, artifacts)
        mock_secho.assert_called_once_with(
            "\n[file: gs://my-bucket/test.pdf]",
            fg="cyan",
            nl=False,
        )
