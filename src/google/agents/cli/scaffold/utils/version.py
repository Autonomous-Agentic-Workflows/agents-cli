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

"""Version checking utilities for the CLI."""

import logging
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PACKAGE_NAME = "google-agents-cli"
# The 0.0.0 sentinel used when a real version can't be determined — an
# uninstalled/dev checkout (get_current_version) or an unreachable PyPI
# (get_latest_version). Not a real release, so it can't be fetched from PyPI.
UNKNOWN_VERSION = "0.0.0"
_UPDATE_CHECK_INTERVAL = 12 * 60 * 60  # 12 hours in seconds
_UPDATE_CHECK_STAMP = Path.home() / ".agents" / ".acli_update_check"
_LATEST_VERSION_CACHE = Path.home() / ".agents" / ".acli_latest_version"


def _update_check_is_due() -> bool:
    """Return True if enough time has elapsed since the last check."""
    try:
        last = float(_UPDATE_CHECK_STAMP.read_text().strip())
        return (time.time() - last) > _UPDATE_CHECK_INTERVAL
    except (OSError, ValueError):
        return True


def _record_update_check() -> None:
    """Write the current timestamp to the stamp file."""
    try:
        _UPDATE_CHECK_STAMP.parent.mkdir(parents=True, exist_ok=True)
        _UPDATE_CHECK_STAMP.write_text(str(time.time()))
    except OSError:
        pass


def get_current_version() -> str:
    """Get the current installed version of the package."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        # Package isn't installed (editable / dev checkout).
        return UNKNOWN_VERSION


def agents_cli_version_pin() -> str:
    """Return the version suffix to pin `google-agents-cli` in generated projects.

    Renders to `@<version>` for released builds and to an empty string for the
    `0.0.0` unknown-version sentinel, so local renders against an uninstalled
    package leave the deploy steps using an unpinned `google-agents-cli`.
    """
    current_version = get_current_version()
    if current_version == UNKNOWN_VERSION:
        return ""
    return f"@{current_version}"


def get_latest_version() -> str:
    """Get the latest version available on PyPI."""
    try:
        # Lazy import requests to speed up CLI startup time
        import requests
        response = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=2)
        if response.status_code == 200:
            return response.json()["info"]["version"]
        return UNKNOWN_VERSION
    except Exception:
        return UNKNOWN_VERSION  # PyPI couldn't be reached


def check_for_updates() -> tuple[bool, str, str]:
    """Check if a newer version of the package is available.

    Returns:
        Tuple of (needs_update, current_version, latest_version)
    """
    # Lazy import packaging.version to speed up CLI startup time
    from packaging import version as pkg_version

    current = get_current_version()
    latest = get_latest_version()

    needs_update = pkg_version.parse(latest) > pkg_version.parse(current)

    return needs_update, current, latest


def _spawn_background_update_check() -> None:
    """Spawn a detached background process to check PyPI for updates."""
    try:
        from google.agents.cli._runner import popen_resolved_detached

        cache_path = _LATEST_VERSION_CACHE.as_posix()
        stamp_path = _UPDATE_CHECK_STAMP.as_posix()

        # Build inline Python code using standard library urllib.request
        # To avoid any extra standard library/version incompatibilities, we use raw string formatting
        # and .as_posix() for Paths (to handle Windows backslashes seamlessly).
        code = (
            "import urllib.request\n"
            "import json\n"
            "import time\n"
            "from pathlib import Path\n"
            "try:\n"
            "    req = urllib.request.Request(\n"
            f"        'https://pypi.org/pypi/{PACKAGE_NAME}/json',\n"
            "        headers={'User-Agent': 'google-agents-cli-update-checker'}\n"
            "    )\n"
            "    with urllib.request.urlopen(req, timeout=5) as response:\n"
            "        if response.status == 200:\n"
            "            data = json.loads(response.read().decode('utf-8'))\n"
            f"            latest = data.get('info', {{}}).get('version', '{UNKNOWN_VERSION}')\n"
            f"            if latest != '{UNKNOWN_VERSION}':\n"
            f"                cache_file = Path({cache_path!r})\n"
            "                cache_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "                cache_file.write_text(latest, encoding='utf-8')\n"
            f"                stamp_file = Path({stamp_path!r})\n"
            "                stamp_file.write_text(str(time.time()), encoding='utf-8')\n"
            "except Exception:\n"
            "    pass\n"
        )

        popen_resolved_detached(
            [sys.executable, "-c", code],
            resolve_executable=False,
        )
    except Exception:
        pass


def display_update_message() -> None:
    """Check for updates and display a message if an update is available."""
    # Instantly read latest cached version if available
    latest = UNKNOWN_VERSION
    try:
        if _LATEST_VERSION_CACHE.is_file():
            latest = _LATEST_VERSION_CACHE.read_text(encoding="utf-8").strip()
    except Exception:
        pass

    current = get_current_version()

    if latest != UNKNOWN_VERSION:
        try:
            from packaging import version as pkg_version
            if pkg_version.parse(latest) > pkg_version.parse(current):
                from rich.console import Console

                console = Console()
                console.print(
                    f"\n[yellow]⚠️  Update available: {current} → {latest}[/]",
                    highlight=False,
                )
                console.print(
                    f"[yellow]Run `uv tool upgrade {PACKAGE_NAME}` to update.[/]",
                    highlight=False,
                )
                console.print(
                    f"[dim]If you installed differently: pip install --upgrade {PACKAGE_NAME} | pipx upgrade {PACKAGE_NAME}[/]",
                    highlight=False,
                )
        except Exception:
            pass

    if _update_check_is_due():
        _record_update_check()
        _spawn_background_update_check()
