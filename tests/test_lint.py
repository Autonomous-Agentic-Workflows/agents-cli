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

from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli.dev.cmd_lint import cmd_lint


def test_cmd_lint_default_success():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_lint.run") as mock_run:
        result = runner.invoke(cmd_lint, [])
        assert result.exit_code == 0
        assert "✓ All code quality checks passed!" in result.output
        assert mock_run.call_count >= 3


def test_cmd_lint_fix_success():
    runner = CliRunner()
    with patch("google.agents.cli.dev.cmd_lint.run") as mock_run:
        result = runner.invoke(cmd_lint, ["--fix"])
        assert result.exit_code == 0
        assert "✓ Code formatting and linting completed." in result.output
        assert mock_run.call_count >= 3
