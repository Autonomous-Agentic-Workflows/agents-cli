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

"""Unit tests for agents-cli playground command banner formatting."""

from unittest.mock import patch

from google.agents.cli.dev.cmd_playground import _print_banner


def test_print_banner_contains_hyperlink():
    url = "http://127.0.0.1:8080/dev-ui/?app=my_agent"
    cmd_args = ["uv", "run", "adk", "web", "."]

    with patch("google.agents.cli.dev.cmd_playground._console.print") as mock_print:
        _print_banner(url, cmd_args)
        mock_print.assert_called_once()
        panel = mock_print.call_args[0][0]
        # Verify the panel renderable body contains Rich link markup
        assert f"[link={url}]{url}[/link]" in panel.renderable
