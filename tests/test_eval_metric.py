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

"""Tests for agents-cli eval metric commands."""

from unittest.mock import patch

from click.testing import CliRunner

from google.agents.cli.eval.cmd_metric import list_metrics


def test_list_metrics_output():
    """Verify list_metrics displays table, count summary, and actionable tip."""
    runner = CliRunner()
    result = runner.invoke(list_metrics)
    assert result.exit_code == 0
    assert "Evaluation" in result.output
    assert "Metrics" in result.output
    assert "Total metrics available:" in result.output
    assert "agents-cli eval grade --metrics <NAME>" in result.output


def test_list_metrics_empty():
    """Verify list_metrics handles empty metrics gracefully."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.eval.cmd_metric.SUPPORTED_PREDEFINED_METRICS", []
    ):
        result = runner.invoke(list_metrics)
        assert result.exit_code == 0
        assert "No built-in evaluation metrics found." in result.output
