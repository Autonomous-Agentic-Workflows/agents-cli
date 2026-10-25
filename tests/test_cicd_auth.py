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

from google.agents.cli.infra._cicd_utils import handle_github_authentication


def test_handle_github_authentication_options_formatting(capsys):
    """Test that handle_github_authentication prints formatted option titles."""
    with patch("click.prompt", return_value="1"), patch("google.agents.cli.infra._cicd_utils.run_command"):
        handle_github_authentication(interactive=True)

    captured = capsys.readouterr()
    assert "Choose an authentication method:" in captured.out
    assert "1. Login with browser" in captured.out
    assert "2. Login with token" in captured.out
