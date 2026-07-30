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
import os
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


def _is_ci() -> bool:
    """Return True when running in a CI/automation environment."""
    return any(
        os.environ.get(var) for var in ("CI", "BUILD_ID", "GITHUB_ACTIONS", "GITLAB_CI")
    )


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


def display_update_message() -> None:
    """Check for updates and display a message if an update is available.

    This function is designed to be completely non-blocking:
    1. It reads the last known 'latest' version from a local cache file.
    2. If a newer version is available compared to the current version, it displays the message.
    3. If the update check interval (12 hours) has elapsed, it spawns a completely detached
       background Python subprocess to query PyPI and update the cache file.
    This ensures that CLI commands never block on synchronous PyPI network requests.
    """
    if _is_ci():
        return

    # 1. Display cached update warning if available
    try:
        current = get_current_version()
        if current != UNKNOWN_VERSION and _LATEST_VERSION_CACHE.exists():
            latest = _LATEST_VERSION_CACHE.read_text(encoding="utf-8").strip()
            if latest and latest != UNKNOWN_VERSION:
                # Lazy import packaging.version and rich to speed up CLI startup time
                from packaging import version as pkg_version
                from rich.console import Console

                if pkg_version.parse(latest) > pkg_version.parse(current):
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
    except Exception as e:
        logging.debug(f"Error checking cached update version: {e}")

    # 2. Trigger asynchronous, detached background check if due
    if _update_check_is_due():
        # Immediately record the check to prevent other concurrent invocations from spawning duplicate processes.
        _record_update_check()

        try:
            import sys
            from google.agents.cli._runner import popen_resolved_detached

            # This script runs in a completely detached python background process.
            # It uses only standard library modules (urllib.request, json, time) to start
            # instantly and performs a non-blocking fetch from PyPI, caching the result
            # and updating the check stamp upon success.
            script = (
                "import urllib.request, json, time, sys\n"
                "from pathlib import Path\n"
                "try:\n"
                "    req = urllib.request.Request('https://pypi.org/pypi/google-agents-cli/json', headers={'User-Agent': 'google-agents-cli-updater'})\n"
                "    with urllib.request.urlopen(req, timeout=2) as r:\n"
                "        if r.status == 200:\n"
                "            version = json.loads(r.read().decode('utf-8'))['info']['version']\n"
                "            cache_file = Path.home() / '.agents' / '.acli_latest_version'\n"
                "            cache_file.parent.mkdir(parents=True, exist_ok=True)\n"
                "            cache_file.write_text(version, encoding='utf-8')\n"
                "            stamp_file = Path.home() / '.agents' / '.acli_update_check'\n"
                "            stamp_file.write_text(str(time.time()), encoding='utf-8')\n"
                "except Exception:\n"
                "    pass\n"
            )

            popen_resolved_detached([sys.executable, "-c", script])
        except Exception as e:
            logging.debug(f"Error spawning background update check: {e}")
