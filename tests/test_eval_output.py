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

"""Unit tests for evaluation completion output formatting and visual styling."""

from unittest.mock import MagicMock

from rich.console import Console

from google.agents.cli.eval.eval_utils import save_evaluation_artifacts


def test_save_evaluation_artifacts_output_formatting(tmp_path):
    """Test that save_evaluation_artifacts prints completion messages with bold green checkmark."""
    mock_console = MagicMock(spec=Console)
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {}
    mock_result.evaluation_dataset = []

    save_evaluation_artifacts(mock_result, str(tmp_path), mock_console)

    printed_lines = [call[0][0] for call in mock_console.print.call_args_list]
    json_saved_msg = next((line for line in printed_lines if "Saved full results to" in line), None)
    assert json_saved_msg is not None
    assert "[bold green]✓ Saved full results to:[/bold green]" in json_saved_msg
