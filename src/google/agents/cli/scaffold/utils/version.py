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
    """Return True if enough time has elapsed since the last check or if cache is missing."""
    if not _LATEST_VERSION_CACHE.exists():
        return True
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


def display_update_message() -> None:
    """Check for updates instantly using cached latest version, and trigger bg check if due."""
    try:
        # 1. Instantly read and display update message from local cache
        if _LATEST_VERSION_CACHE.exists():
            try:
                latest = _LATEST_VERSION_CACHE.read_text().strip()
                current = get_current_version()
                if latest and latest != UNKNOWN_VERSION and current != UNKNOWN_VERSION:
                    from packaging import version as pkg_version
                    if pkg_version.parse(latest) > pkg_version.parse(current):
                        # Lazy import Console to speed up CLI startup time
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
            except Exception as e:
                logging.debug(f"Error reading/parsing cached version: {e}")

        # 2. Spawn a detached background process to fetch the latest version if check is due
        if _update_check_is_due():
            import sys
            from google.agents.cli._runner import popen_resolved_detached

            cmd = [
                sys.executable,
                "-c",
                (
                    "import urllib.request, json, sys, time; "
                    "from pathlib import Path; "
                    "try: "
                    "    req = urllib.request.Request('https://pypi.org/pypi/' + sys.argv[1] + '/json', headers={'User-Agent': 'Mozilla/5.0'}); "
                    "    with urllib.request.urlopen(req, timeout=2) as response: "
                    "        if response.status == 200: "
                    "            data = json.loads(response.read().decode()); "
                    "            latest = data['info']['version']; "
                    "            cache = Path(sys.argv[2]); "
                    "            cache.parent.mkdir(parents=True, exist_ok=True); "
                    "            cache.write_text(latest); "
                    "            stamp = Path(sys.argv[3]); "
                    "            stamp.parent.mkdir(parents=True, exist_ok=True); "
                    "            stamp.write_text(str(time.time())); "
                    "except Exception: "
                    "    pass"
                ),
                PACKAGE_NAME,
                _LATEST_VERSION_CACHE.as_posix(),
                _UPDATE_CHECK_STAMP.as_posix(),
            ]
            popen_resolved_detached(cmd)

    except Exception as e:
        # Don't let version checking errors affect the CLI
        logging.debug(f"Error checking for updates: {e}")
