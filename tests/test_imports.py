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

"""Tests for import optimization and prevention of eager heavy imports."""

import subprocess
import sys


def test_no_heavy_imports_on_main_import():
    """Ensure that importing google.agents.cli.main does not eagerly load heavy dependencies."""
    # Run a clean python subprocess to test imports in isolation
    code = """
import sys
import google.agents.cli.main

heavy_modules = ["requests", "rich", "yaml", "packaging"]
loaded = [mod for mod in heavy_modules if mod in sys.modules]
if loaded:
    print(",".join(loaded))
    sys.exit(1)
sys.exit(0)
"""
    res = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Heavy modules eagerly loaded: {res.stdout.strip()}"
