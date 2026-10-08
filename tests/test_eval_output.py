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

"""Unit tests for eval completion output formatting across eval commands."""

import inspect

from google.agents.cli.eval import cmd_analyze, cmd_dataset, cmd_generate


def _get_fn_source(func):
    fn = getattr(func, "callback", func)
    return inspect.getsource(fn)


def test_eval_analyze_completion_format():
    """Verify cmd_analyze includes bold green checkmark in completion message."""
    src = _get_fn_source(cmd_analyze.cmd_analyze)
    assert "[bold green]✓ Detailed analysis results saved to:[/bold green]" in src


def test_eval_dataset_completion_format():
    """Verify cmd_synthesize includes bold green checkmark in completion message."""
    src = _get_fn_source(cmd_dataset.cmd_synthesize)
    assert "[bold green]✓ Traces saved to:[/bold green]" in src


def test_eval_generate_completion_format():
    """Verify cmd_generate includes bold green checkmark in completion message."""
    src = _get_fn_source(cmd_generate.cmd_generate)
    assert "[bold green]✓ Traces saved to:[/bold green]" in src
