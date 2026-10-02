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


def test_list_metrics_success():
    """Test list_metrics displays metric table, summary count, and usage tip."""
    runner = CliRunner()
    result = runner.invoke(list_metrics)
    assert result.exit_code == 0
    assert "Built-in Evaluation" in result.output
    assert "Metric Name" in result.output
    assert "Total:" in result.output
    assert "metrics available" in result.output
    assert "Tip: Pass metrics to grade using" in result.output


def test_list_metrics_empty():
    """Test list_metrics handles empty metric list gracefully."""
    runner = CliRunner()
    with patch(
        "google.agents.cli.eval.cmd_metric.SUPPORTED_PREDEFINED_METRICS", []
    ):
        result = runner.invoke(list_metrics)
        assert result.exit_code == 0
        assert "No built-in evaluation metrics found." in result.output
