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

"""Test ensuring CLI startup does not regress by eagerly loading heavy dependencies."""

import subprocess
import sys


def test_no_heavy_imports_on_startup():
    # Run in a clean subprocess to ensure isolated import environment.
    # PYTHONPATH is passed through by the pytest execution environment.
    cmd = [
        sys.executable,
        "-c",
        "import sys; import google.agents.cli.main; "
        "heavy = [m for m in sys.modules if any(m == x or m.startswith(x + '.') for x in ('yaml', 'requests', 'rich', 'packaging'))]; "
        "print(','.join(heavy))",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    loaded_heavy_modules = result.stdout.strip()
    assert not loaded_heavy_modules, (
        f"Heavy modules eagerly imported on startup: {loaded_heavy_modules}"
    )
