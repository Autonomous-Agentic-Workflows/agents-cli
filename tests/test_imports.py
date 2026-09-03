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

"""Tests to verify that importing CLI modules does not eagerly load heavy packages."""

import subprocess
import sys


def test_no_heavy_eager_imports():
    """Verify that importing google.agents.cli.main does not import heavy packages."""
    # We run a separate, clean Python process to ensure no previous imports pollute sys.modules.
    code = """
import sys
import google.agents.cli.main

heavy_modules = ["requests", "yaml", "rich", "packaging"]
loaded = [m for m in heavy_modules if any(k == m or k.startswith(m + ".") for k in sys.modules)]
if loaded:
    print(f"Error: Heavy modules loaded eagerly on import: {loaded}")
    sys.exit(1)
print("OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Import check failed: {result.stdout}\n{result.stderr}"


def test_cmd_run_no_heavy_eager_imports():
    """Verify that importing google.agents.cli.run.cmd_run does not eagerly load heavy packages."""
    code = """
import sys
import google.agents.cli.run.cmd_run

heavy_modules = ["httpx", "requests", "a2a"]
loaded = [m for m in heavy_modules if any(k == m or k.startswith(m + ".") for k in sys.modules)]
if loaded:
    print(f"Error: Heavy modules loaded eagerly on import of cmd_run: {loaded}")
    sys.exit(1)
print("OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Import check failed: {result.stdout}\n{result.stderr}"


def test_agent_runtime_a2a_no_heavy_eager_imports():
    """Verify that importing google.agents.cli._agent_runtime_a2a does not eagerly load a2a."""
    code = """
import sys
import google.agents.cli._agent_runtime_a2a

heavy_modules = ["a2a"]
loaded = [m for m in heavy_modules if any(k == m or k.startswith(m + ".") for k in sys.modules)]
if loaded:
    print(f"Error: Heavy modules loaded eagerly on import: {loaded}")
    sys.exit(1)
print("OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Import check failed: {result.stdout}\n{result.stderr}"
