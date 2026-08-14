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
            version_str = response.json()["info"]["version"]
            # Write to cache for consistency
            try:
                _LATEST_VERSION_CACHE.parent.mkdir(parents=True, exist_ok=True)
                _LATEST_VERSION_CACHE.write_text(version_str, encoding="utf-8")
            except OSError:
                pass
            return version_str
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

    This function is completely non-blocking: it displays any update warning
    instantly using a cached version file, and triggers a detached background
    subprocess to check PyPI for updates only when the interval has elapsed.
    """
    if _update_check_is_due():
        # Record immediately to prevent other invocations from spawning duplicate background checks
        _record_update_check()
        try:
            from google.agents.cli._runner import popen_resolved_detached

            # This detached background script uses python's stdlib urllib to fetch
            # the latest version from PyPI and save it to the cache file, ensuring
            # zero startup delay/blocking network requests in the CLI main path.
            code = (
                "import json, urllib.request, sys; "
                "from pathlib import Path; "
                "try: "
                f"    req = urllib.request.Request('https://pypi.org/pypi/{PACKAGE_NAME}/json', headers={{'User-Agent': 'google-agents-cli-update-checker'}}); "
                "    with urllib.request.urlopen(req, timeout=5) as r: "
                "        data = json.loads(r.read().decode('utf-8')); "
                "        latest = data['info']['version']; "
                "        cache = Path(sys.argv[1]); "
                "        cache.parent.mkdir(parents=True, exist_ok=True); "
                "        cache.write_text(latest, encoding='utf-8'); "
                "except Exception: "
                "    pass"
            )
            popen_resolved_detached(
                [
                    sys.executable,
                    "-c",
                    code,
                    str(_LATEST_VERSION_CACHE),
                ],
                resolve_executable=False,
            )
        except Exception as e:
            # Don't let background spawning errors affect the CLI
            logging.debug(f"Error starting background update check: {e}")

    # Display update warning instantly if a cached version shows an update is available
    try:
        if _LATEST_VERSION_CACHE.is_file():
            latest = _LATEST_VERSION_CACHE.read_text(encoding="utf-8").strip()
            current = get_current_version()
            if latest and latest != UNKNOWN_VERSION and current != UNKNOWN_VERSION:
                # Lazy import packaging.version to speed up CLI startup time
                from packaging import version as pkg_version

                needs_update = pkg_version.parse(latest) > pkg_version.parse(current)
                if needs_update:
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
        # Don't let version checking errors affect the CLI
        logging.debug(f"Error displaying update message: {e}")
